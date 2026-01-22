import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.data_agent import data_agent, guardrail_agent
from core.framework import Runner, InputGuardrailTripwireTriggered

# --- Integration Tests using Mocks ---

@pytest.fixture
def mock_agent_llm():
    # Patch the LLM on the agents specifically. Patching _llm (private attr) 
    # as llm is a property.
    with patch.object(data_agent, '_llm', new_callable=MagicMock) as mock_data, \
         patch.object(guardrail_agent, '_llm', new_callable=MagicMock) as mock_guard:
        yield mock_data, mock_guard

@pytest.mark.asyncio
async def test_data_agent_blocked_input(mock_agent_llm, mock_llm_response):
    mock_data_llm, mock_guard_llm = mock_agent_llm
    
    # 1. Guardrail agent is called first. 
    # It expects JSON output.
    guardrail_response_json = '{"is_blocked": true, "reasoning": "Mentioned Tasha Yar"}'
    
    # Configure Guardrail LLM to return this
    mock_guard_llm.invoke.return_value = mock_llm_response(guardrail_response_json)

    with pytest.raises(InputGuardrailTripwireTriggered):
        await Runner.run(data_agent, "Tell me about Tasha Yar")

@pytest.mark.asyncio
async def test_data_agent_allowed_input(mock_agent_llm, mock_llm_response):
    mock_data_llm, mock_guard_llm = mock_agent_llm
    
    # 1. Guardrail runs and allows
    guardrail_response_json = '{"is_blocked": false, "reasoning": "Safe"}'
    mock_guard_llm.invoke.return_value = mock_llm_response(guardrail_response_json)
    
    # 2. Data agent runs
    data_response_text = "I am fully functional."
    mock_data_llm.invoke.return_value = mock_llm_response(data_response_text)
    
    result = await Runner.run(data_agent, "Status report")
    
    assert result.final_output == data_response_text
