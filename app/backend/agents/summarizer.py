from config import client, model
from state_types import AppState


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
