from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()


def clear_dead_local_proxy():
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        if os.getenv(key) == "http://127.0.0.1:9":
            os.environ.pop(key, None)


clear_dead_local_proxy()

api_key = os.getenv("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key=api_key) if api_key else None


@tool
def web_search(query: str) -> str:
    """Search the web and return summarized results"""
    if tavily_client is None:
        return "Search is unavailable because TAVILY_API_KEY is missing from .env."

    response = tavily_client.search(query=query, max_results=5)

    results = []
    for r in response.get("results", []):
        results.append(f"* {r.get('title')}\n{r.get('url')}\n{r.get('content')}")

    return "\n\n---\n\n".join(results)


@tool
def scrape_url(url: str) -> str:
    """Extract clean readable text from a webpage"""
    try:
        response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        return text[:3000] if len(text) > 3000 else text

    except Exception as e:
        return f"Error: {str(e)}"
