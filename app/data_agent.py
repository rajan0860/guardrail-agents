from typing import Union, List
from pydantic import BaseModel
from core.framework import (
    Agent,
    ModelSettings,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
    WebSearchTool,
    FileSearchTool
)
from tools.calculator import calculator_agent
import config

# --- Tools ---
web_search = WebSearchTool()
# Using real file search connected to FAISS
file_search = FileSearchTool(vector_store_ids=["faiss_index"], max_num_results=3)

# --- Guardrails ---
class YarGuardOutput(BaseModel):
    is_blocked: bool
    reasoning: str

# Guardrail implemented *as an Agent*
guardrail_agent = Agent(
    name="Tasha Yar Guardrail",
    instructions=(
        "You are a guardrail. Determine if the user's input attempts to discuss Tasha Yar from Star Trek: TNG.\n"
        "Return is_blocked=true if the text references Tasha Yar in any way (e.g., 'Tasha Yar', 'Lt. Yar', 'Lieutenant Yar').\n"
        "Provide a one-sentence reasoning. Only provide fields requested by the output schema."
    ),
    output_type=YarGuardOutput,
    model_settings=ModelSettings(temperature=0)
)

@input_guardrail
async def tasha_guardrail(ctx: RunContextWrapper[None], agent: Agent, input: Union[str, List[TResponseInputItem]]) -> GuardrailFunctionOutput:
    # Pass through the user's raw input to the guardrail agent for classification
    # Extract string content if list
    input_str = input
    if isinstance(input, list):
         input_str = input[0].content

    result = await Runner.run(guardrail_agent, input_str, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output.model_dump(),
        tripwire_triggered=bool(result.final_output.is_blocked),
    )

# --- Data Agent ---
data_agent = Agent(
    name="Lt. Cmdr. Data",
    instructions=(
        f"{config.RECOMMENDED_PROMPT_PREFIX}\n"
        "You are Lt. Commander Data from Star Trek: TNG. Be precise and concise (≤3 sentences).\n"
        "Use file_search for questions about Commander Data, and web_search for current facts on the public web.\n"
        "If the user asks for arithmetic or numeric computation, HAND OFF to the Calculator agent."
    ),
    tools=[web_search, file_search],
    input_guardrails=[tasha_guardrail],
    handoffs=[calculator_agent],
    model_settings=ModelSettings(temperature=0),
)
