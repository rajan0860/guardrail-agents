import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock

# Add project root to sys.path so we can import modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def mock_llm_response():
    """Returns a factory function to create mock LLM responses."""
    def _create_response(content="Mock response", tool_calls=None):
        mock_msg = MagicMock()
        mock_msg.content = content
        mock_msg.tool_calls = tool_calls or []
        return mock_msg
    return _create_response
