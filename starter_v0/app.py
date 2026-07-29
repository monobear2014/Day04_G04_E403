from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)

st.set_page_config(page_title="Research Agent", layout="wide")

PROVIDER_NAME = "openrouter"
VERSION_LABEL = "v0"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
HISTORY_WINDOW = 5
MAX_TOOL_ROUNDS = 4


@st.cache_resource
def get_provider():
    return make_provider(PROVIDER_NAME)


def load_agent_config():
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(TOOLS_PATH)
    openai_tools = to_openai_tools(tool_declarations)
    artifact_version = build_artifact_version(VERSION_LABEL, SYSTEM_PROMPT_PATH, TOOLS_PATH)
    return system_prompt, openai_tools, artifact_version


if "history" not in st.session_state:
    st.session_state.history = []
if "turns" not in st.session_state:
    st.session_state.turns = []
if "transcript_id" not in st.session_state:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    st.session_state.transcript_id = "_".join([safe_slug(VERSION_LABEL), safe_slug(PROVIDER_NAME), timestamp])

provider = get_provider()
system_prompt, openai_tools, artifact_version = load_agent_config()
selected_model = getattr(provider, "default_model", None)
transcript_path = TRANSCRIPTS_DIR / f"{st.session_state.transcript_id}.transcript.json"

st.title("Research Agent — Local Demo")
st.caption(
    f"provider={PROVIDER_NAME} · model={selected_model} · "
    f"artifact_version={artifact_version.artifact_version}"
)

for turn in st.session_state.turns:
    with st.chat_message("user"):
        st.write(turn["user"])
    with st.chat_message("assistant"):
        st.write(turn["assistant_text"])
        for round_record in turn["rounds"]:
            for call, result in zip(round_record["tool_calls"], round_record["tool_results"]):
                with st.expander(f"🔧 {call['name']}({call['args']})"):
                    st.json(result["result"])

user_text = st.chat_input("Hỏi agent (vd: tìm tin AI hôm nay)...")

if user_text:
    with st.chat_message("user"):
        st.write(user_text)

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, HISTORY_WINDOW),
        {"role": "user", "content": user_text},
    ]

    turn_record: dict[str, Any] = {
        "turn_index": len(st.session_state.turns) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    with st.chat_message("assistant"):
        with st.spinner("Đang xử lý..."):
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=None,
                    max_tool_rounds=MAX_TOOL_ROUNDS,
                )
                turn_record.update(result)
                assistant_text = result["assistant_text"]
                st.session_state.history.append({"role": "user", "content": user_text})
                st.session_state.history.append({"role": "assistant", "content": assistant_text})
            except Exception as exc:
                assistant_text = f"ERROR: {type(exc).__name__}: {exc}"
                turn_record.update({"status": "provider_error", "error": assistant_text})

        st.write(assistant_text)
        for round_record in turn_record["rounds"]:
            for call, tool_result in zip(round_record["tool_calls"], round_record["tool_results"]):
                with st.expander(f"🔧 {call['name']}({call['args']})"):
                    st.json(tool_result["result"])

    turn_record["ended_at"] = now_iso()
    st.session_state.turns.append(turn_record)

    transcript = {
        "transcript_id": st.session_state.transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": PROVIDER_NAME,
        "model": selected_model,
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": HISTORY_WINDOW,
        "max_tool_rounds": MAX_TOOL_ROUNDS,
        "created_at": st.session_state.turns[0]["started_at"],
        "turns": st.session_state.turns,
    }
    write_transcript(transcript_path, transcript)
    st.caption(f"Transcript saved: {transcript_path}")
