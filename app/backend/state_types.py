from typing import Annotated, List, TypedDict
import operator


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
