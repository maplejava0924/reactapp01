import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://filmarks.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
}


def get_synopsis_from_meta(detail_url: str) -> str:
    try:
        res = requests.get(detail_url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag and meta_tag.get("content"):
            description = meta_tag["content"].strip()
            # 特定の定型句を含む場合はその後ろのあらすじ部分を抜き出す
            split_keywords = [
                "、内容・ネタバレ、あらすじ、予告編・予告動画、公開映画館情報、公開スケジュール、監督・出演者の関連映画情報",
                "件のレビュー(口コミ・感想・評価)",
            ]
            for keyword in split_keywords:
                if keyword in description:
                    description = description.split(keyword)[-1].strip()
            return description
    except Exception as e:
        print(f"[ERROR] {detail_url} の取得に失敗しました: {e}")
    return "あらすじ記載なし"


# 最大10本まで上映中の映画の情報を取得する
# nowで上映中の映画を取得するか、公開予定の映画を取得するか選択する
def fetch_filmarks_movies(limit: int = 10, now: bool = True) -> list[str]:
    try:
        # 上映中 or 公開予定の映画URLを切り替え
        if now:
            # 上映中の映画一覧
            list_url = f"{BASE_URL}/list/now"
        else:
            # 公開予定の映画一覧
            list_url = f"{BASE_URL}/list/coming"

        res = requests.get(list_url, headers=HEADERS)
        soup = BeautifulSoup(res.content, "html.parser")
        movies = soup.find_all("div", class_="js-cassette")
        results = []
        for i, movie in enumerate(movies):
            if i >= limit:
                break
            title_tag = movie.find("h3", class_="p-content-cassette__title")
            title = title_tag.text.strip() if title_tag else "タイトル記載なし"

            genre_list = []
            genres_section = movie.find("ul", class_="genres")
            if genres_section:
                genre_list = [li.text.strip() for li in genres_section.find_all("li")]

            release_info = movie.find("div", class_="p-content-cassette__info-main")
            release_date = "公開日不明"
            if release_info:
                span = release_info.find("span")
                if span:
                    release_date = span.text.strip()

            score_tag = movie.find("div", class_="c-rating__score")
            score = score_tag.text.strip() if score_tag else "スコアなし"

            readmore_tag = movie.find("a", class_="p-content-cassette__readmore")
            if readmore_tag and readmore_tag.get("href"):
                detail_url = BASE_URL + readmore_tag["href"]
                time.sleep(0.5)  # 負荷軽減のためスリープ
                synopsis = get_synopsis_from_meta(detail_url)
            else:
                synopsis = "あらすじ記載なし"

            movie_text = (
                f"【映画{i + 1}】\n"
                f"タイトル: {title}\n"
                f"ジャンル: {', '.join(genre_list) if genre_list else 'ジャンル記載なし'}\n"
                f"公開日: {release_date}\n"
                f"評価スコア: {score}\n"
                f"あらすじ: {synopsis}"
            )
            results.append(movie_text)
        return results
    except Exception as e:
        return [f"Filmarksの取得に失敗しました: {str(e)}"]
