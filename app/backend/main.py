from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, List, TypedDict
import operator
import asyncio
import logging
import json
import re
import os
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langsmith import Client
from pathlib import Path
import requests

# LangChain
model = ChatOpenAI(model="gpt-4o-mini")

# LangSmith
client = Client()

# FastAPI
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

# キャラ定義用JSONファイルの読み込み
with open(Path("character_profiles.json"), "r", encoding="utf-8") as f:
    ALL_CHARACTER_PROFILES = json.load(f)

# 司会の最初の発言も入れて6回
MAX_SPEAK_COUNT = 6


# --- 状態定義 ---
class AppState(TypedDict):
    thema: str  # 会話のテーマ（司会やエージェントが発言する際に使用）
    user_message: str  # ユーザが送信フォームで入力した内容。クエリパラメータで受け取り、司会に読み込ませる。
    genres: List[
        str
    ]  # ユーザがフォームで入力した内容。クエリパラメータで受け取り、司会に読み込ませる。
    seen_movies: str  # ユーザがフォームで入力した内容。クエリパラメータで受け取り、司会に読み込ませる。
    character_names: List[
        str
    ]  # ユーザがフォームで入力した内容。クエリパラメータで受け取り、司会L、スピーカーに読み込ませる。
    character_profiles: dict[str, dict[str, str]]
    last_speaker: str  # 直前の発言者
    last_comment: str  # 直前の発言内容（要約エージェントがこれを要約する）
    summary: Annotated[
        List[dict], operator.add
    ]  # 要約された発言のリスト（司会が最後のまとめに使う）。要約結果に発言者の名前を含むようdict型にする。
    speak_count: int  # 全体の発言数（MAX_SPEAK_COUNT で上限をチェック）
    next_speaker: str  # 次に話すキャラクターの名前（司会が決める）
    summary_done: bool  # 直前の発言が要約済みかどうか（Trueなら要約済、Falseなら要約未） LangGraphのグラフ遷移判定に使用
    is_summary: bool  # このメッセージが要約文であるか否か　フロントエンドのホワイトボードへの記載要否を制御


# --- 司会（フロー制御） ---
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


# 検索キーワードをインプットに検索結果を返す
def search_tavily(query: str) -> List[str]:
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


# --- 発言エージェント ---
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
    }

    prompt = client.pull_prompt("maplejava/speaker-template")
    prompt_value = prompt.invoke(inputs)

    response = model.invoke(prompt_value)

    return {
        "last_speaker": speaker,
        "last_comment": response.content,
        "speak_count": speak_count + 1,
        "summary_done": False,
        "is_summary": False,
    }


# --- 要約エージェント ---
def summarizer_agent(state: AppState):
    last_speaker = state.get("last_speaker")
    last_comment = state.get("last_comment")
    thema = state.get("thema")

    inputs = {
        "thema": thema,
        "last_comment": last_comment,
        "last_speaker": last_speaker,
    }
    prompt = client.pull_prompt("maplejava/summarizer-template")
    prompt_value = prompt.invoke(inputs)

    response = model.invoke(prompt_value)

    return {
        "last_speaker": last_speaker,
        "summary": [{"speaker": last_speaker, "text": response.content}],
        "summary_done": True,
        "is_summary": True,
    }


# --- フロー分岐 ---
def route_next(state: AppState):
    if state["next_speaker"] == "no_one":
        return "end"
    elif not state["summary_done"]:
        return "summarize"
    else:
        return "speak"


# --- LangGraph構築 ---
graph = StateGraph(AppState)
graph.add_node("moderator", moderator)
graph.add_node("speaker", speaker_agent)
graph.add_node("summarizer", summarizer_agent)

graph.set_entry_point("moderator")

# ▼ 条件分岐の説明付きエッジ設定
# moderatorノードにて次にどこへ進むかをstateに基づいて判断：
# - summary_done が False → summarizer に移動して要約
# - summary_done が True → speaker に移動して次の発言
# - next_speaker == no_one → 会話終了
graph.add_conditional_edges(
    "moderator",
    route_next,
    {
        "speak": "speaker",
        "summarize": "summarizer",
        "end": END,
    },
)

graph.add_edge("speaker", "summarizer")
graph.add_edge("summarizer", "moderator")

# LangGraphのフローをコンパイル（ここではまだ実行しない）
flow = graph.compile()


@app.get("/chat/stream")
async def chat_stream(request: Request):
    # フロントエンドから送られてきたデータの取り出し
    user_message = request.query_params.get("user_message", "")
    genres_raw = request.query_params.get("genres", "")
    genre_list = [
        g.strip() for g in genres_raw.split(",") if g.strip()
    ]  # ←空やスペースも除く

    seen_movies = request.query_params.get("seen_movies", "")
    characters = request.query_params.get("characters", "")
    selected_names = characters.split(",")
    # 選ばれたキャラクターのプロフィール
    character_profiles = {name: ALL_CHARACTER_PROFILES[name] for name in selected_names}

    async def event_generator():
        # Stateの初期値の決定
        state = {
            "thema": "最近おすすめの映画",
            "user_message": user_message,
            "summary": [],
            "speak_count": 0,
            "next_speaker": "",
            "summary_done": False,
            "last_comment": "",
            "last_speaker": "",
            "is_summary": False,
            "genres": genre_list,
            "seen_movies": seen_movies,
            "character_names": selected_names,
            "character_profiles": character_profiles,
        }

        # フローの実行（LangGraphの状態管理が開始）
        # 状態が変わるたびにチャット用の内容を yield でフロントへストリーミング送信
        async for event in flow.astream(state):
            if await request.is_disconnected():
                break

            logging.info(f"event: {event}")

            # LangGraphから返るeventは常に {ノード名: {...}} の形なので、1階層下を抽出
            value = next(iter(event.values()))

            message = value.get("last_comment")
            summary = value.get("summary")
            speaker = value.get("last_speaker")
            is_summary = value.get("is_summary")

            if message:
                payload = {
                    "last_speaker": speaker,  # Noneのときに備えて
                    "text": message,
                    "is_summary": is_summary,
                }
                yield f"data: {json.dumps(payload)}\n\n"

            if summary:
                for item in summary:
                    payload = {
                        "last_speaker": item["speaker"],
                        "text": item["text"],
                        "is_summary": is_summary,
                    }
                    yield f"data: {json.dumps(payload)}\n\n"

            await asyncio.sleep(0.3)  # 一気にメッセージが出ないようにちょっと待つ

        # SSEの終了をフロントエンドに伝える
        yield "event: end\ndata: END_OF_STREAM\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
