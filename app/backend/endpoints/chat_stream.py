from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio
import json
import logging
from pathlib import Path
from graph.chat_graph import build_graph

router = APIRouter()

with open(Path("character_profiles.json"), "r", encoding="utf-8") as f:
    ALL_CHARACTER_PROFILES = json.load(f)


@router.get("/chat/stream")
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
    flow = build_graph()  # LangGraph フローの初期化

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
