from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, List, TypedDict
import operator
import random
import asyncio
import logging
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


app = FastAPI()

# Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- キャラ定義・定数 ---
CHARACTER_PROFILES = {
    "A子": {
        "性別": "女性",
        "年齢": "30代",
        "職業": "会社員",
        "趣味": "音楽鑑賞",
        "性格": "落ち着いた性格で、じっくり物事を考えて発言します。",
    },
    "B太": {
        "性別": "男性",
        "年齢": "20代",
        "職業": "大学生",
        "趣味": "テレビゲーム",
        "性格": "明るく、前向きな性格です。",
    },
    "C助": {
        "性別": "男性",
        "年齢": "40代",
        "職業": "会社役員",
        "趣味": "ゴルフ",
        "性格": "温厚で、話しやすい雰囲気を持っています。",
    },
}
CHARACTER_NAMES = list(CHARACTER_PROFILES.keys())

# 司会の最初の発言も入れて6回
MAX_SPEAK_COUNT = 6


# --- 状態定義 ---
class AppState(TypedDict):
    thema: str  # 会話のテーマ（司会やエージェントが発言する際に使用）
    last_comment: str  # 直前の発言内容（要約エージェントがこれを要約する）
    summary: Annotated[
        List[str], operator.add
    ]  # 要約された発言のリスト（司会が最後のまとめに使う）
    speak_count: int  # 全体の発言数（MAX_SPEAK_COUNT で上限をチェック）
    next_speaker: str  # 次に話すキャラクターの名前（司会が決める）
    summary_done: (
        bool  # 直前の発言が要約済みかどうか（Trueなら次は発言、Falseなら要約）
    )


# --- 司会（フロー制御） ---
def moderator(state: AppState):
    model = ChatOpenAI(model="gpt-4o-mini")
    thema = state["thema"]
    speak_count = state["speak_count"]

    # 初回の導入
    if speak_count == 0:
        system_message = "あなたは会話の司会進行役です。"
        human_message = f"""
以下のテーマでこれから会話を始めます。
参加者が話しやすくなるような導入コメントを司会として一文で出力してください。

# テーマ
{thema}
"""
        response = model.invoke(
            [SystemMessage(content=system_message), HumanMessage(content=human_message)]
        )
        content = f"司会: {response.content}"
        logging.info(content)
        return {
            "last_comment": content,
            "speak_count": speak_count + 1,
            "summary_done": False,
        }

    # 会話まとめ
    if speak_count >= MAX_SPEAK_COUNT:
        summary_lines = state.get("summary", [])
        summary_text = "\n".join(summary_lines)

        system_message = "あなたは会議の司会者で、議論のまとめが得意です。"
        human_message = f"""
以下は「{thema}」というテーマについて参加者が出した要約コメントです。
これらをもとに、誰がどのような魅力的なゲームの話をしていたかを振り返ってください。
そして最後に会話を締めくくるような自然な司会コメントを一文で出力してください。

# 要約リスト
{summary_text}
"""
        response = model.invoke(
            [SystemMessage(content=system_message), HumanMessage(content=human_message)]
        )
        content = f"司会: {response.content}"
        logging.info(content)
        return {"last_comment": content, "next_speaker": "no_one"}

    # 次の発言者を決める
    next_speaker = random.choice(CHARACTER_NAMES)
    system_message = "あなたは会話の司会進行役です。"
    human_message = f"""
以下のテーマについて、すでに何人かが意見を話しました。
次に「{next_speaker}」さんに発言を促す自然な司会の一言を出力してください。
テーマ: {thema}
"""
    response = model.invoke(
        [SystemMessage(content=system_message), HumanMessage(content=human_message)]
    )
    content = f"司会: {response.content}"
    logging.info(content)

    return {"last_comment": content, "next_speaker": next_speaker}


# --- 発言エージェント ---
def speaker_agent(state: AppState):
    speaker = state.get("next_speaker")
    thema = state.get("thema", "")
    speak_count = state.get("speak_count", 0)

    profile = CHARACTER_PROFILES.get(speaker, {})
    system_message = f"""あなたは以下のようなキャラクターになりきってください。
---
名前: {speaker}
性別: {profile.get("性別")}
年齢: {profile.get("年齢")}
職業: {profile.get("職業")}
趣味: {profile.get("趣味")}
性格: {profile.get("性格")}
---
そのキャラクターとして、「{thema}」というテーマについて自分の意見を述べてください。
話し言葉で、自然に1〜2文程度で簡潔に述べてください。
"""

    model = ChatOpenAI(model="gpt-4o-mini")
    response = model.invoke([SystemMessage(content=system_message)])
    content = f"{speaker}の意見: {response.content}"
    logging.info(content)

    return {
        "last_comment": content,
        "speak_count": speak_count + 1,
        "summary_done": False,
    }


# --- 要約エージェント ---
def summarizer_agent(state: AppState):
    model = ChatOpenAI(model="gpt-4o-mini")
    last_comment = state.get("last_comment")
    thema = state.get("thema")

    system_message = "あなたは発言を自然な日本語で簡潔に要約するアシスタントです。"
    human_message = f"""
以下は「{thema}」というテーマについての直近の発言です。
この発言を自然な形で一文で要約してください。誰が発言したのかも要約に含めてください。
要約文の前には「要約:」をつけてください。

# 発言
{last_comment}
"""
    response = model.invoke(
        [SystemMessage(content=system_message), HumanMessage(content=human_message)]
    )
    summary = response.content
    logging.info(summary)
    return {"summary": [summary], "summary_done": True}


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
# moderatorが次にどこへ進むかをstateに基づいて判断：
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

# --- 実行 ---
flow = graph.compile()


@app.get("/chat/stream")
async def chat_stream(request: Request):
    async def event_generator():
        # Stateの初期値の決定
        state = {
            "thema": "最近おすすめのゲーム",
            "summary": [],
            "speak_count": 0,
            "next_speaker": "",
            "summary_done": False,
            "last_comment": "",
        }

        async for event in flow.astream(state):
            if await request.is_disconnected():
                break

            logging.info(f"event: {event}")

            # LangGraphから返るeventは常に {ノード名: {...}} の形なので、1階層下を抽出
            value = next(iter(event.values()))

            message = value.get("last_comment")
            summary = value.get("summary")

            if message:
                yield f"data: {message}\n\n"

            if summary:
                for line in summary:
                    yield f"data: {line}\n\n"

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
