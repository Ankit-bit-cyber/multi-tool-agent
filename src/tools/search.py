"""Search tool — SerpAPI / DuckDuckGo search wrapper."""

import os
import requests
from typing import List, Dict, Any, Optional
from .base import tool


class SearchTool:
    """Web search tool using SerpAPI or DuckDuckGo."""
    
    SERPAPI_BASE = "https://serpapi.com/search"
    DUCKDUCKGO_BASE = "https://api.duckduckgo.com/"
    
    @staticmethod
    @tool(
        name="search",
        description="Search the web for information",
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query",
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return",
                }
            },
            "required": ["query"],
        }
    )
    def search(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web.
        
        Args:
            query: Search query
            num_results: Number of results
            
        Returns:
            List of search results
        """
        api_key = os.getenv("SERPAPI_KEY")
        
        if api_key:
            return SearchTool._search_serpapi(query, num_results, api_key)
        else:
            return SearchTool._search_duckduckgo(query, num_results)
    
    @staticmethod
    def _search_serpapi(query: str, num_results: int, api_key: str) -> List[Dict[str, Any]]:
        """Search using SerpAPI."""
        try:
            response = requests.get(
                SearchTool.SERPAPI_BASE,
                params={"q": query, "api_key": api_key, "num": num_results},
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("organic_results", [])[:num_results]:
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet"),
                })
            return results
        except Exception as e:
            return [{"error": f"SerpAPI search failed: {str(e)}"}]
    
    @staticmethod
    def _search_duckduckgo(query: str, num_results: int) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo API."""
        try:
            response = requests.get(
                SearchTool.DUCKDUCKGO_BASE,
                params={"q": query, "format": "json"},
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("Results", [])[:num_results]:
                results.append({
                    "title": item.get("Text"),
                    "link": item.get("FirstURL"),
                    "snippet": item.get("Text"),
                })
            return results
        except Exception as e:
            return [{"error": f"DuckDuckGo search failed: {str(e)}"}]
