from tavily import TavilyClient

client = TavilyClient("TAVILY_API_KEY")

response = client.search(
    query="latest AI news",
    search_depth="advanced"
)

print(response)
