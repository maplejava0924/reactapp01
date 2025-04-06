from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, List, TypedDict
import operator
import asyncio
import logging
import json
import re
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
        "年齢": "20代",
        "職業": "会社員",
        "趣味": "音楽鑑賞",
        "性格": "落ち着いた性格で、じっくり物事を考えて発言します。B太と喧嘩中です。B太の発言には厳しくあたります。",
    },
    "B太": {
        "性別": "男性",
        "年齢": "20代",
        "職業": "大学生",
        "趣味": "テレビゲーム",
        "性格": "明るく、前向きな性格です。A子と喧嘩中です。B太はA子に怒られるとうんざりした様子になります。",
    },
    "C助": {
        "性別": "男性",
        "年齢": "40代",
        "職業": "会社役員",
        "趣味": "ゴルフ",
        "性格": "温厚で、話しやすい雰囲気を持っています。A子とB太が喧嘩中であることは知っていますが、蚊帳の外という感じです。「若い人は元気だなぁ」と楽観的な反応をします。",
    },
}
CHARACTER_NAMES = list(CHARACTER_PROFILES.keys())

# 司会の最初の発言も入れて6回
MAX_SPEAK_COUNT = 6


# --- 状態定義 ---
class AppState(TypedDict):
    thema: str  # 会話のテーマ（司会やエージェントが発言する際に使用）
    user_message: str  # ユーザが送信フォームで入力した内容。クエリパラメータで受け取り、司会LLMに読み込ませる。
    genres: str  # ユーザがフォームで入力した内容。クエリパラメータで受け取り、司会LLMに読み込ませる。
    seen_movies: str  # ユーザがフォームで入力した内容。クエリパラメータで受け取り、司会LLMに読み込ませる。
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
    model = ChatOpenAI(model="gpt-4o-mini")
    thema = state["thema"]
    user_message = state.get("user_message", "")
    genres = state.get("genres", "")
    seen_movies = state.get("seen_movies", "")
    speak_count = state["speak_count"]
    last_speaker = "司会"

    # 初回の導入
    if speak_count == 0:
        system_message = "あなたは会話の司会進行役です。"
        human_message = f"""
以下のテーマでこれから会話を始めます。
ユーザからのインプットに触れ、議論をどういう方向性にするか検討し、参加者が話しやすくなるような導入コメントを出力してください。
ここでいう「ユーザ」とは、以下のテーマで議論する様子を見たいと思っている、この議論の聴講者です。
あなたの役割はユーザからの指示の意図を汲みこれからの議論がユーザの意図に沿うものになるようコントロールすることです。

# テーマ
{thema}

# ユーザが見たいジャンル
{genres if genres else "（指定なし）"}

# ユーザが今まで見た映画
{seen_movies if seen_movies else "（特になし）"}

# ユーザからの補足メッセージ
{user_message if user_message else "特になし"}
"""
        response = model.invoke(
            [SystemMessage(content=system_message), HumanMessage(content=human_message)]
        )
        logging.info(f"{last_speaker}: {response.content}")
        return {
            "last_speaker": last_speaker,
            "last_comment": response.content,
            "speak_count": speak_count + 1,
            "summary_done": False,
            "is_summary": False,
        }

    # 会話まとめ
    if speak_count >= MAX_SPEAK_COUNT:
        summary_items = state.get("summary", [])
        summary_text = "\n".join(
            [f"{item['speaker']}：{item['text']}" for item in summary_items]
        )

        system_message = "あなたは会議の司会者で、議論のまとめが得意です。"
        human_message = f"""
以下は「{thema}」というテーマについて参加者が出した要約コメントです。
これらをもとに、誰がどのような魅力的な話をしていたかを振り返ってください。
そして最後に会話を締めくくるような自然な司会コメントを一文で出力してください。

# 要約リスト
{summary_text}
"""
        response = model.invoke(
            [SystemMessage(content=system_message), HumanMessage(content=human_message)]
        )
        logging.info(f"{last_speaker}: {response.content}")
        return {
            "last_speaker": last_speaker,
            "last_comment": response.content,
            "next_speaker": "no_one",
            "is_summary": False,
        }

    # 次の発言者を決める
    last_comment = state.get("last_comment")
    summary_items = state.get("summary", [])
    summary_text = "\n".join(
        [f"{item['speaker']}：{item['text']}" for item in summary_items]
    )

    system_message = "あなたは会話の司会進行役です。以下の会話の流れを見て、直前のコメントに反応するコメントを出しつつ、次に発言すべき人を1人選び、司会としてコメントしてください。"

    human_message = f"""
テーマ: {thema}
議論が特定の話題に偏ってきた場合は、次の話者に対して違った観点での発言を求めるようにしてください。
※ 必ずまだ発言していない人を優先してください。発言者名は以下から選んでください：
{", ".join(CHARACTER_NAMES)}

直前のコメント：
{last_comment}

今までの会話要約：
{summary_text}

以下のフォーマットで出力してください：

#次の話者：{{話者名}}
#コメント：{{自然な司会コメント}}

"""

    response = model.invoke(
        [SystemMessage(content=system_message), HumanMessage(content=human_message)]
    )
    logging.info(f"{last_speaker}: {response.content}")

    response_text = response.content

    match_speaker = re.search(r"#次の話者：(.+)", response_text)
    match_comment = re.search(r"#コメント：(.+)", response_text)

    next_speaker = match_speaker.group(1).strip() if match_speaker else "未定"
    last_comment = (
        match_comment.group(1).strip() if match_comment else response_text
    )  # fallback

    return {
        "last_speaker": last_speaker,
        "last_comment": last_comment,
        "next_speaker": next_speaker,
        "is_summary": False,
    }


# --- 発言エージェント ---
def speaker_agent(state: AppState):
    speaker = state.get("next_speaker")
    thema = state.get("thema", "")
    speak_count = state.get("speak_count", 0)
    summary_items = state.get("summary", [])
    summary_text = "\n".join(
        [f"{item['speaker']}：{item['text']}" for item in summary_items]
    )

    last_comment = state.get("last_comment")

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
そのキャラクターとして、「{thema}」というテーマについて会話履歴を参考に議論の流れを汲んで、話し言葉で自分の意見を述べてください。
直前のコメントについては軽く触れてもよいですが、議論が停滞気味になってきたら新しい話題をしてください。
ほかの人に賛同するだけではなく、自分としての意見を述べるようにしてください。
自分ばかり発言を求められた場合は、司会を注意してください。
「C助：」のような誰が話したかの表記は不要です。なりきったキャラクターのセリフのみを出力してください。

直前のコメント：{last_comment}
会話履歴：{summary_text}

"""

    model = ChatOpenAI(model="gpt-4o-mini")
    response = model.invoke([SystemMessage(content=system_message)])
    logging.info(f"{speaker}の意見: {response.content}")

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
    model = ChatOpenAI(model="gpt-4o-mini")
    last_comment = state.get("last_comment")
    thema = state.get("thema")

    system_message = "あなたは発言を自然な日本語で簡潔に要約するアシスタントです。"
    human_message = f"""
以下は「{thema}」というテーマについての直近の発言です。
この発言を、要点ごとに文章短く分けて要約してください。出力は1文でお願いします。
・発言者の名前や「〜と述べた」は不要です。
・発言の中で重要な事実・意見・主張を3文以内にまとめてください。
・自然な日本語のまま短く切ってください（1文40文字以内が目安）。
・敬語は避けてください。

# 発言
{last_comment}

# 発言者
{last_speaker}

"""
    response = model.invoke(
        [SystemMessage(content=system_message), HumanMessage(content=human_message)]
    )
    logging.info(response.content)

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
    user_message = request.query_params.get("user_message", "")
    genres = request.query_params.get("genres", "")
    seen_movies = request.query_params.get("seen_movies", "")

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
            "genres": genres,
            "seen_movies": seen_movies,
        }

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
