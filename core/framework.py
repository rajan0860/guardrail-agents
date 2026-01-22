import logging
import asyncio
from typing import List, Callable, Any, Optional, Union, Dict, Type
from pydantic import BaseModel, ConfigDict, PrivateAttr, Field
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, BaseMessage, AIMessage
from langchain_core.tools import tool, BaseTool, StructuredTool
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
import config

# --- Core Types mimicking OpenAI Agents SDK ---

class ModelSettings(BaseModel):
    temperature: float = 0.0

class RunConfig(BaseModel):
    pass

class GuardrailFunctionOutput(BaseModel):
    output_info: dict
    tripwire_triggered: bool

class InputGuardrailTripwireTriggered(Exception):
    pass

class TResponseInputItem(BaseModel):
    content: str
    role: str = "user"

from typing import Generic, TypeVar

T = TypeVar("T")

class RunContextWrapper(Generic[T]):
    def __init__(self, context: dict):
        self.context = context

class RunResult(BaseModel):
    final_output: Union[str, BaseModel, Any]
    last_agent: Optional['Agent'] = None

# --- Decorators ---

def function_tool(func: Callable) -> Callable:
    """Decorator to mark a function as a tool."""
    return tool(func)

def input_guardrail(func: Callable) -> Callable:
    """Decorator for input guardrails."""
    return func

# --- Agent Class ---

class Agent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    instructions: str
    tools: List[Any] = []
    input_guardrails: List[Any] = []
    handoffs: List['Agent'] = []
    model_settings: ModelSettings = Field(default_factory=ModelSettings)
    output_type: Optional[Any] = None # using Any to avoid strict valid
    
    _llm: Any = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        
        # Initialize LLM
        if self.output_type:
             self._llm = ChatOllama(
                model=config.OLLAMA_MODEL, 
                temperature=self.model_settings.temperature,
                format="json" # Force JSON mode for structured output
            )
        else:
            self._llm = ChatOllama(
                model=config.OLLAMA_MODEL,
                temperature=self.model_settings.temperature,
            ).bind_tools(self.tools)

    @property
    def llm(self):
        return self._llm

    def __repr__(self):
        return f"<Agent name={self.name}>"

# --- Runner Class ---

class Runner:
    @staticmethod
    async def run(agent: Agent, input_str: str, context: dict = None) -> RunResult:
        if context is None:
            context = {}
            
        print(f"\n[Runner] Start: {agent.name} | Input: {input_str[:50]}...")

        # 1. Run Input Guardrails
        ctx_wrapper = RunContextWrapper(context)
        for guard in agent.input_guardrails:
            # Prepare input item list as expected by some guardrails
            input_items = [TResponseInputItem(content=input_str)]
            
            # Execute guardrail
            print(f"[Runner] Checking guardrail: {guard.__name__}")
            # Guardrails in this SDK seem to be async
            result: GuardrailFunctionOutput = await guard(ctx_wrapper, agent, input_items)
            
            if result.tripwire_triggered:
                print(f"[Runner] Tripwire triggered by {guard.__name__}!")
                raise InputGuardrailTripwireTriggered(f"Guardrail {guard.__name__} triggered.")

        # 2. Convert handoffs to tools (simple logic: explicit handoff instructions usually ok)
        # For this shim, we'll just let the LLM decide to call a "handoff tool" if we were fancy,
        # but for now we'll just run the agent.
        
        currentState = "processing"
        currentAgent = agent
        messages = [
            SystemMessage(content=currentAgent.instructions),
            HumanMessage(content=input_str)
        ]
        
        while currentState == "processing":
            # Invoke LLM
            # If we expect structured output, we add format instructions
            if currentAgent.output_type:
                 messages[0].content += f"\n\nOutput JSON matching this schema: {currentAgent.output_type.model_json_schema()}"
            
            response = currentAgent.llm.invoke(messages)
            messages.append(response)
            
            # Helper to parse JSON if needed
            if currentAgent.output_type and isinstance(response.content, str):
                try:
                    import json
                    data = json.loads(response.content)
                    final_obj = currentAgent.output_type.model_validate(data)
                    return RunResult(final_output=final_obj, last_agent=currentAgent)
                except Exception as e:
                    print(f"[Runner] JSON parse error: {e}")
                    # Fallback to string
            
            if response.tool_calls:
                print(f"[{currentAgent.name}] invoking tools: {response.tool_calls}")
                for tool_call in response.tool_calls:
                    # Check if it's a handoff (name matches an agent)
                    target_agent = next((a for a in currentAgent.handoffs if a.name == tool_call["name"]), None)
                    if target_agent:
                        print(f"[Runner] Handoff to {target_agent.name}")
                        currentAgent = target_agent
                        # Reset messages for new agent but keep context? 
                        # Simplification: Just Run the new agent with the last message?
                        # Or just append a system message saying "You are now X"?
                        # Let's simple-recurse for now or just switch context
                        messages = [
                            SystemMessage(content=currentAgent.instructions),
                            HumanMessage(content=input_str) # Re-feed input? Or context?
                        ]
                        continue

                    # Normal tool
                    selected_tool = next((t for t in currentAgent.tools if t.name == tool_call["name"]), None)
                    if selected_tool:
                        tool_result = selected_tool.invoke(tool_call["args"])
                        print(f"[{currentAgent.name}] Tool output: {tool_result}")
                        messages.append(ToolMessage(
                            tool_call_id=tool_call["id"],
                            content=str(tool_result),
                            name=tool_call["name"]
                        ))
                
                # If we processed tools (and didn't handoff), invoke again for final answer
                final_response = currentAgent.llm.invoke(messages)
                return RunResult(final_output=final_response.content, last_agent=currentAgent)
            
            # No tool calls, just return text
            return RunResult(final_output=response.content, last_agent=currentAgent)

# --- Placeholders for tools user referenced ---

class FileSearchTool(BaseTool):
    name: str = "file_search"
    description: str = "Search local files."
    _vector_store: Optional[FAISS] = PrivateAttr(default=None)
    
    def __init__(self, vector_store_ids=None, max_num_results=3):
        super().__init__()
        # In a real setup, we would load based on IDs. For this simple refactor, we load the main index.
        try:
            embeddings = OllamaEmbeddings(model=config.EMBEDDING_MODEL)
            if config.VECTOR_STORE_PATH.exists():
                self._vector_store = FAISS.load_local(
                    folder_path=str(config.VECTOR_STORE_PATH), 
                    embeddings=embeddings,
                    allow_dangerous_deserialization=True # Local file, safe
                )
            else:
                print(f"Warning: Vector store not found at {config.VECTOR_STORE_PATH}")
        except Exception as e:
            print(f"Error loading vector store: {e}")
    
    def _run(self, query: str):
        if not self._vector_store:
            return "Error: Vector store not available."
        
        docs = self._vector_store.similarity_search(query, k=3)
        return "\n".join([d.page_content for d in docs])

# Helper Set Key
def set_default_openai_key(key: str):
    pass
