import csv
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
VERSION_LOG_PATH = ARTIFACTS_DIR / "version_log.csv"
load_lab_env(ROOT)

st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="wide")

PROVIDER_NAME = "openrouter"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
HISTORY_WINDOW = 5
MAX_TOOL_ROUNDS = 4

EXAMPLE_QUESTIONS = [
    "Tìm 5 tin tức AI nổi bật hôm nay",
    "Tìm repo GitHub về RAG agent",
    "Các bài đăng mới nhất của tài khoản OpenAI",
    "Đăng bản tin này lên Telegram giúp mình",
]

st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; max-width: 900px; }
    .agent-subtitle { color: var(--text-color, #6b7280); opacity: 0.75; margin-top: -0.6rem; }
    div[data-testid="stChatMessage"] { padding-bottom: 0.15rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


MAIN_VERSIONS = ["v0", "v1", "v2"]


def load_version_logs() -> dict[str, dict[str, str]]:
    all_versions: dict[str, dict[str, str]] = {}
    if VERSION_LOG_PATH.exists():
        try:
            with open(VERSION_LOG_PATH, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    v = row.get("version", "").strip()
                    if v:
                        all_versions[v] = row
        except Exception:
            pass

    filtered: dict[str, dict[str, str]] = {}
    for v in MAIN_VERSIONS:
        if v in all_versions:
            filtered[v] = all_versions[v]
        else:
            filtered[v] = {
                "version": v,
                "reason": "Main System Version",
                "metric_after": "N/A",
                "artifact_version": f"{v}+hash",
            }
    return filtered


@st.cache_resource
def get_provider():
    return make_provider(PROVIDER_NAME)


def load_agent_config(version_label: str):
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(TOOLS_PATH)
    openai_tools = to_openai_tools(tool_declarations)
    artifact_version = build_artifact_version(version_label, SYSTEM_PROMPT_PATH, TOOLS_PATH)
    return system_prompt, tool_declarations, openai_tools, artifact_version


def new_session(version_label: str = "v7") -> None:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    st.session_state.history = []
    st.session_state.turns = []
    st.session_state.pending_query = None
    st.session_state.transcript_id = "_".join([safe_slug(version_label), safe_slug(PROVIDER_NAME), timestamp])
    st.session_state.current_version = version_label


version_logs = load_version_logs()
version_keys = list(version_logs.keys())
default_index = version_keys.index("v7") if "v7" in version_keys else (len(version_keys) - 1 if version_keys else 0)

if "current_version" not in st.session_state:
    st.session_state.current_version = version_keys[default_index] if version_keys else "v0"

if "history" not in st.session_state:
    new_session(st.session_state.current_version)

try:
    current_idx = version_keys.index(st.session_state.current_version)
except ValueError:
    current_idx = default_index

with st.sidebar:
    st.markdown("### 🏆 Team G04")
    c1, c2 = st.columns(2)
    c1.metric("Eval base", "20/20")
    c2.metric("Eval nhóm", "10/10")
    st.divider()
    st.markdown("### ⚙️ Cấu hình")
    st.markdown(f"**Provider**  \n`{PROVIDER_NAME}`")

    selected_version = st.selectbox(
        "📌 Phiên bản chính (Version)",
        options=version_keys,
        index=current_idx,
        help="Chọn 1 trong 3 phiên bản chính có tác động lớn nhất (v0, v3, v7)",
    )

    if selected_version != st.session_state.current_version:
        new_session(selected_version)
        st.rerun()

    provider = get_provider()
    system_prompt, tool_declarations, openai_tools, artifact_version = load_agent_config(selected_version)
    selected_model = getattr(provider, "default_model", None)
    transcript_path = TRANSCRIPTS_DIR / f"{st.session_state.transcript_id}.transcript.json"

    v_info = version_logs.get(selected_version, {})
    custom_art_ver = v_info.get("artifact_version", "").strip() or artifact_version.artifact_version

    st.markdown(f"**Model**  \n`{selected_model}`")
    st.markdown(f"**Artifact version**  \n`{custom_art_ver}`")

    if v_info.get("metric_after"):
        st.caption(f"🎯 **Accuracy:** `{v_info['metric_after']}`")
    if v_info.get("reason"):
        st.caption(f"📝 **Lý do thay đổi:** {v_info['reason']}")

    st.divider()
    with st.expander("📜 3 Phiên bản tác động lớn nhất"):
        for vk, info in version_logs.items():
            acc = info.get("metric_after", "N/A")
            st.markdown(f"**{vk}** — Accuracy: `{acc}`")
            if info.get("reason"):
                st.caption(info["reason"])
            st.markdown("---")

    st.markdown(f"### 🛠️ Tools ({len(tool_declarations)})")
    for decl in tool_declarations:
        st.markdown(f"- `{decl['name']}`")
    st.divider()
    if st.button("🔄 Đoạn chat mới", use_container_width=True):
        new_session(selected_version)
        st.rerun()

st.title("🔎 Research Agent")
st.markdown(
    "<p class='agent-subtitle'>Tìm kiếm, tổng hợp và hỏi lại khi thiếu thông tin — có tool trace cho từng bước.</p>",
    unsafe_allow_html=True,
)
st.divider()


def render_tool_calls(round_record: dict[str, Any]) -> None:
    for call, tool_result in zip(round_record["tool_calls"], round_record["tool_results"]):
        args_str = ", ".join(f"{k}={v!r}" for k, v in call["args"].items())
        result = tool_result.get("result", {})
        has_error = isinstance(result, dict) and result.get("error")
        badge = "❌" if has_error else "✅"
        with st.expander(f"{badge} 🔧 `{call['name']}({args_str})`"):
            st.json(result)


if not st.session_state.turns:
    st.markdown("**Thử ngay với một câu hỏi mẫu:**")
    cols = st.columns(2)
    for i, question in enumerate(EXAMPLE_QUESTIONS):
        if cols[i % 2].button(question, use_container_width=True):
            st.session_state.pending_query = question
    st.divider()

for turn in st.session_state.turns:
    with st.chat_message("user"):
        st.write(turn["user"])
    with st.chat_message("assistant", avatar="🔎"):
        st.write(turn["assistant_text"])
        for round_record in turn["rounds"]:
            render_tool_calls(round_record)

user_text = st.chat_input("Hỏi agent (vd: tìm tin AI hôm nay)...") or st.session_state.pop("pending_query", None)

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

    with st.chat_message("assistant", avatar="🔎"):
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
            render_tool_calls(round_record)

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
    st.caption(f"💾 Transcript saved: `{transcript_path.name}`")
