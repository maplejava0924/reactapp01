import requests
import os


# 検索キーワードをインプットに検索結果を返す
def search_tavily(query: str) -> list[str]:
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": os.environ["TAVILY_API_KEY"],
        "query": query,
        "search_depth": "advanced",
        "max_results": 3,
        "include_answer": False,
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    results = response.json().get("results", [])
    return [
        f"{item['title']}（{item['url']}）\n{item.get('content', '')}"
        for item in results
    ]
