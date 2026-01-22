import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from core.framework import Agent, Runner, InputGuardrailTripwireTriggered, GuardrailFunctionOutput, function_tool

# --- Mocks and Helpers ---

@pytest.fixture
def mock_chat_ollama():
    with patch('core.framework.ChatOllama') as mock:
        yield mock

@function_tool
def simple_tool(arg: str) -> str:
    """A simple tool for testing."""
    return f"Processed {arg}"

# --- Test Agent Initialization ---

def test_agent_initialization(mock_chat_ollama):
    agent = Agent(name="TestAgent", instructions="Do stuff")
    assert agent.name == "TestAgent"
    assert agent.llm is not None
    mock_chat_ollama.assert_called()

# --- Test Runner ---

@pytest.mark.asyncio
async def test_runner_simple_execution(mock_chat_ollama, mock_llm_response):
    # Setup agent
    agent = Agent(name="TestAgent", instructions="Be helpful")
    
    # Setup mock LLM response
    mock_llm_instance = agent.llm
    mock_llm_instance.invoke.return_value = mock_llm_response("Hello there!")

    # Run
    result = await Runner.run(agent, "Hi")
    
    assert result.final_output == "Hello there!"
    assert result.last_agent == agent

@pytest.mark.asyncio
async def test_runner_with_guardrail_tripwire():
    # Define a guardrail that trips
    async def tripping_guardrail(ctx, agent, input_items):
        return GuardrailFunctionOutput(output_info={}, tripwire_triggered=True)
    
    agent = Agent(
        name="GuardedAgent", 
        instructions="Secure",
        input_guardrails=[tripping_guardrail]
    )

    with pytest.raises(InputGuardrailTripwireTriggered):
        await Runner.run(agent, "bad input")

@pytest.mark.asyncio
async def test_runner_tool_execution(mock_chat_ollama, mock_llm_response):
    agent = Agent(name="ToolAgent", instructions="Use tools", tools=[simple_tool])
    mock_llm = agent.llm
    
    # Sequence of responses:
    # 1. LLM requests tool call
    # 2. LLM receives tool output and gives final answer
    
    msg_tool_call = mock_llm_response("", tool_calls=[{
        "name": "simple_tool",
        "args": {"arg": "data"},
        "id": "call_1"
    }])
    
    msg_final = mock_llm_response("Here is the result: Processed data")
    
    mock_llm.invoke.side_effect = [msg_tool_call, msg_final]

    result = await Runner.run(agent, "process data")
    
    assert "Processed data" in str(result.final_output)
    assert mock_llm.invoke.call_count == 2
