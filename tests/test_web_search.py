import pytest
from unittest.mock import patch, MagicMock
from tools.web_search import WebSearchTool

@patch('tools.web_search.DDGS')
def test_web_search_success(mock_ddgs_cls):
    # Setup mock
    mock_ddgs_instance = mock_ddgs_cls.return_value
    mock_ddgs_instance.text.return_value = [
        {'title': 'Result 1', 'href': 'http://example.com/1', 'body': 'Description 1'},
        {'title': 'Result 2', 'href': 'http://example.com/2', 'body': 'Description 2'}
    ]

    tool = WebSearchTool()
    result = tool.invoke("test query")

    # Verify interaction
    mock_ddgs_instance.text.assert_called_with("test query", max_results=3)
    
    # Verify output format
    assert "Title: Result 1" in result
    assert "Link: http://example.com/1" in result
    assert "Title: Result 2" in result

@patch('tools.web_search.DDGS')
def test_web_search_no_results(mock_ddgs_cls):
    mock_ddgs_instance = mock_ddgs_cls.return_value
    mock_ddgs_instance.text.return_value = []

    tool = WebSearchTool()
    result = tool.invoke("weird query")
    
    assert result == "No results found."

@patch('tools.web_search.DDGS')
def test_web_search_exception(mock_ddgs_cls):
    mock_ddgs_instance = mock_ddgs_cls.return_value
    mock_ddgs_instance.text.side_effect = Exception("API Error")

    tool = WebSearchTool()
    result = tool.invoke("crash query")

    assert "Error performing search: API Error" in result
