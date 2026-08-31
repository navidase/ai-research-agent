import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")

if not api_key:
    raise RuntimeError("TAVILY_API_KEY is not set")

client = TavilyClient(api_key=api_key)


def search(query):
    results = client.search(
        query=query,
        max_results=5
    )

    return results["results"]