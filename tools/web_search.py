from duckduckgo_search import DDGS
from core.framework import BaseTool

class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Search the web for information using DuckDuckGo."
    
    def _run(self, query: str):
        try:
            print(f"DEBUG: Searching web for '{query}'")
            results = DDGS().text(query, max_results=3)
            if not results:
                return "No results found."
            
            # Format results
            formatted_results = []
            for r in results:
                formatted_results.append(f"Title: {r['title']}\nLink: {r['href']}\nSnippet: {r['body']}")
            
            return "\n\n".join(formatted_results)
        except Exception as e:
            return f"Error performing search: {e}"
