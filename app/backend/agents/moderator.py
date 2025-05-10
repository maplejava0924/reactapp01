import re
from config import client, model, MAX_SPEAK_COUNT
from state_types import AppState


def moderator(state: AppState):
    thema = state["thema"]
    user_message = state.get("user_message", "")
    genres_list = state.get("genres", [])
    genres_text = ", ".join(genres_list) if genres_list else "（指定なし）"
    seen_movies = state.get("seen_movies", "")
    speak_count = state["speak_count"]
    character_names = state["character_names"]
    character_profiles = state["character_profiles"]

    # 司会に憑依させるキャラクター（最初に選ばれたキャラ）
    last_speaker = character_names[0]

    # 誰も話してないならfirst-templateを実行
    if speak_count == 0:
        profile = character_profiles.get(last_speaker, {})
        # ChatPromptTemplateに食わせる辞書型のInput
        inputs = {
            "name": last_speaker,
            "gender": profile["性別"],
            "age": profile["年齢"],
            "job": profile["職業"],
            "hobby": profile["趣味"],
            "personality": profile["性格"],
            "thema": thema,
            "genres": genres_text,
            "seen_movies": seen_movies if seen_movies else "（特になし）",
            "user_message": user_message if user_message else "特になし",
        }
        # LangSmith Prompt呼び出し
        prompt = client.pull_prompt("maplejava/moderator-first-template")
        prompt_value = prompt.invoke(inputs)

        response = model.invoke(prompt_value)

        return {
            "last_speaker": last_speaker,
            "last_comment": response.content,
            "speak_count": speak_count + 1,
            "summary_done": False,
            "is_summary": False,
        }

    # 会話の上限数に達したならsummary-templateを実行
    if speak_count >= MAX_SPEAK_COUNT:
        summary_items = state.get("summary", [])
        profile = character_profiles.get(last_speaker, {})
        inputs = {
            "name": last_speaker,
            "gender": profile["性別"],
            "age": profile["年齢"],
            "job": profile["職業"],
            "hobby": profile["趣味"],
            "personality": profile["性格"],
            "thema": thema,
            "summary_text": "\n".join(
                [f"{item['speaker']}：{item['text']}" for item in summary_items]
            ),
        }

        prompt = client.pull_prompt("maplejava/moderator-summary-template")
        prompt_value = prompt.invoke(inputs)
        response = model.invoke(prompt_value)

        return {
            "last_speaker": last_speaker,
            "last_comment": response.content,
            "next_speaker": "no_one",
            "is_summary": False,
        }

    # 上記いずれでもないならnext-speaker-templateを実行
    summary_items = state.get("summary", [])
    # 司会キャラ（最初のキャラ）は除く
    candidate_names = [name for name in character_names if name != last_speaker]

    profile = character_profiles.get(last_speaker, {})
    inputs = {
        "name": last_speaker,
        "gender": profile["性別"],
        "age": profile["年齢"],
        "job": profile["職業"],
        "hobby": profile["趣味"],
        "personality": profile["性格"],
        "thema": thema,
        "character_names": ", ".join(candidate_names),
        "summary_text": "\n".join(
            [f"{item['speaker']}：{item['text']}" for item in summary_items]
        ),
    }
    prompt = client.pull_prompt("maplejava/moderator-next-speaker-template")
    prompt_value = prompt.invoke(inputs)

    response = model.invoke(prompt_value)

    response_text = response.content

    # LLMの回答から必要な情報を抽出
    match_speaker = re.search(r"次の話者：(.+)", response_text)
    match_comment = re.search(r"コメント：(.+)", response_text)

    next_speaker = match_speaker.group(1).strip() if match_speaker else "未定"
    last_comment = match_comment.group(1).strip() if match_comment else response_text

    return {
        "last_speaker": last_speaker,
        "last_comment": last_comment,
        "next_speaker": next_speaker,
        "is_summary": False,
    }
