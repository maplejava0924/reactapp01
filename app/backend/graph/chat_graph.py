from langgraph.graph import StateGraph, END
from state_types import AppState
from agents.moderator import moderator
from agents.speaker import speaker_agent
from agents.summarizer import summarizer_agent


# --- フロー分岐 ---
def route_next(state: AppState):
    if state["next_speaker"] == "no_one":
        return "end"
    elif not state["summary_done"]:
        return "summarize"
    else:
        return "speak"


# --- LangGraph構築 ---
def build_graph():
    graph = StateGraph(AppState)
    graph.add_node("moderator", moderator)
    graph.add_node("speaker", speaker_agent)
    graph.add_node("summarizer", summarizer_agent)
    graph.set_entry_point("moderator")

    # ▼ 条件分岐
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
    return graph.compile()
