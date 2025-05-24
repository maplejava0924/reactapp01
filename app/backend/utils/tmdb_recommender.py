# --- utils/tmdb_recommender.py ---
import requests
import os

API_KEY = os.environ["TMDb_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"


def search_movie_id(title, language="ja-JP"):
    url = f"{BASE_URL}/search/movie"
    params = {"api_key": API_KEY, "query": title.strip(), "language": language}
    response = requests.get(url, params=params)
    results = response.json().get("results", [])
    return results[0]["id"] if results else None


def get_movie_details(movie_id, language="ja-JP"):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {"api_key": API_KEY, "language": language}
    response = requests.get(url, params=params)
    return response.json()


def get_recommended_movies(movie_id, language="ja-JP"):
    url = f"{BASE_URL}/movie/{movie_id}/recommendations"
    params = {"api_key": API_KEY, "language": language, "page": 1}
    response = requests.get(url, params=params)
    return response.json().get("results", [])


def get_recommendations_from_seen_movies(seen_movies_str, max_per_movie=2):
    seen_movies = [
        title.strip() for title in seen_movies_str.split(",") if title.strip()
    ]
    grouped_recommendations = []

    for source_title in seen_movies:
        movie_id = search_movie_id(source_title)
        if not movie_id:
            continue
        recommended = get_recommended_movies(movie_id)
        formatted_recommendations = []

        for movie in recommended[:max_per_movie]:
            details = get_movie_details(movie["id"])
            overview = details.get("overview", "").strip()
            if not overview:
                continue
            title = details.get("title", "タイトル不明")
            release_date = details.get("release_date", "日付不明")
            genres = [g["name"] for g in details.get("genres", [])]
            formatted_recommendations.append(
                f"- {title}（{release_date}）\n  ジャンル: {', '.join(genres)}\n  {overview}"
            )

        if formatted_recommendations:
            grouped_text = (
                f"【{source_title}】を見た人がよく見ている映画：\n"
                + "\n\n".join(formatted_recommendations)
            )
            grouped_recommendations.append(grouped_text)

    return grouped_recommendations


print(get_recommendations_from_seen_movies("名探偵コナン,レミーのおいしいレストラン"))
