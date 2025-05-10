from config import client, model
from utils.tavily import search_tavily
from state_types import AppState
from utils.filmarks import fetch_filmarks_movies


def speaker_agent(state: AppState):
    speaker = state.get("next_speaker")
    summary_items = state.get("summary", [])
    character_profiles = state["character_profiles"]
    profile = character_profiles.get(speaker, {})
    speak_count = state["speak_count"]
    thema = state.get("thema", "")
    last_comment = state.get("last_comment", "")
    genres = state.get("genres", [])
    tool_results = []

    # Web検索エージェント tavilyの使用
    if speak_count == 1:
        first_genre = genres[0] if genres else "映画"
        user_query = f"{first_genre} 映画 オススメ"

        try:
            tool_results = search_tavily(user_query)
        except Exception as e:
            tool_results = ["検索に失敗しました：" + str(e)]

        prompt = client.pull_prompt("maplejava/speaker-template")

    # trend分析エージェント filmarksのスクレイピング
    elif speak_count == 2:
        tool_results = fetch_filmarks_movies()
        prompt = client.pull_prompt("maplejava/speaker-trend")

    else:
        prompt = client.pull_prompt("maplejava/speaker-template")

    # ▼ prompt用のinputsを作成
    inputs = {
        "name": speaker,
        "gender": profile["性別"],
        "age": profile["年齢"],
        "job": profile["職業"],
        "hobby": profile["趣味"],
        "personality": profile["性格"],
        "thema": thema,
        "last_comment": last_comment,
        "summary_text": "\n".join(
            [f"{item['speaker']}：{item['text']}" for item in summary_items]
        ),
        "tool_results": "\n".join(tool_results)
        if tool_results
        else "特に検索は行っていません。",
        "genres": ", ".join(genres) if genres else "ジャンル指定なし",
    }

    prompt_value = prompt.invoke(inputs)

    response = model.invoke(prompt_value)

    return {
        "last_speaker": speaker,
        "last_comment": response.content,
        "speak_count": speak_count + 1,
        "summary_done": False,
        "is_summary": False,
    }
