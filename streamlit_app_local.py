import asyncio
import importlib
import json
import os
import threading
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import load_dotenv, set_key
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part


APP_NAME = "HEPARA"
SESSION_ID = "streamlit_session"
ENV_PATH = Path(".env")
DISABLED_MCP_PATH = "__hepara_streamlit_mcp_disabled__.json"

GOOGLE_MODEL_OPTIONS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

OLLAMA_MODEL_OPTIONS = [
    "llama3",
    "llama3.1",
    "llama3.2",
    "qwen2.5",
    "mistral",
    "gemma2",
    "deepseek-r1",
]

CONFIG_KEYS = (
    "GOOGLE_API_KEY",
    "AUTHOR",
    "CATEGORIES",
    "GOOGLE_MODEL",
    "OLLAMA_MODEL",
    "PDF_PATH",
    "ARXIVFLOW_KEYWORD_BACKEND",
)


def run_async(coro: Any) -> Any:
    """Run an async ADK call from Streamlit's synchronous script context."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    result: dict[str, Any] = {}

    def runner() -> None:
        try:
            result["value"] = asyncio.run(coro)
        except Exception as exc:  # pragma: no cover - defensive bridge
            result["error"] = exc

    thread = threading.Thread(target=runner)
    thread.start()
    thread.join()

    if "error" in result:
        raise result["error"]
    return result.get("value")


def load_initial_environment() -> None:
    load_dotenv(ENV_PATH)
    defaults = {
        "GOOGLE_API_KEY": "",
        "AUTHOR": "",
        "CATEGORIES": "",
        "GOOGLE_MODEL": "gemini-2.5-flash",
        "OLLAMA_MODEL": "llama3",
        "PDF_PATH": "./pdf/",
        "ARXIVFLOW_KEYWORD_BACKEND": "ollama",
    }
    for key, default in defaults.items():
        st.session_state.setdefault(f"config_{key}", os.getenv(key, default))


def model_value(options: list[str], selected: str, custom: str) -> str:
    return custom.strip() if selected == "Custom" else selected.strip()


def option_index(options: list[str], value: str) -> int:
    return options.index(value) if value in options else len(options)


def current_config() -> dict[str, str]:
    return {
        "GOOGLE_API_KEY": st.session_state.get("config_GOOGLE_API_KEY", "").strip(),
        "AUTHOR": st.session_state.get("config_AUTHOR", "").strip(),
        "CATEGORIES": st.session_state.get("config_CATEGORIES", "").strip(),
        "GOOGLE_MODEL": st.session_state.get("config_GOOGLE_MODEL", "").strip() or "gemini-2.5-flash",
        "OLLAMA_MODEL": st.session_state.get("config_OLLAMA_MODEL", "").strip(),
        "PDF_PATH": st.session_state.get("config_PDF_PATH", "").strip() or "./pdf/",
        "ARXIVFLOW_KEYWORD_BACKEND": "ollama",
    }


def apply_environment(config: dict[str, str]) -> None:
    for key, value in config.items():
        if value:
            os.environ[key] = value
        else:
            os.environ.pop(key, None)
    os.environ["MCP_PATH"] = DISABLED_MCP_PATH
    os.environ.pop("SKILL_PATH", None)


def save_environment(config: dict[str, str]) -> None:
    ENV_PATH.touch(exist_ok=True)
    for key, value in config.items():
        set_key(ENV_PATH, key, value, quote_mode="auto")


def reload_agent_modules():
    import hepara.agent
    import hepara.prompt
    import hepara.subagents.arxiv_agent.agent
    import hepara.subagents.arxiv_agent.tools
    import hepara.subagents.faq_agent.agent
    import hepara.subagents.faq_agent.prompt
    import hepara.subagents.faq_agent.tools
    import hepara.subagents.inspirehep_agent.agent
    import hepara.subagents.inspirehep_agent.prompt
    import hepara.subagents.inspirehep_agent.tools
    import hepara.subagents.mcp_agent.agent
    import hepara.subagents.mcp_agent.prompt
    import hepara.subagents.mcp_agent.subagents
    import hepara.subagents.mcp_agent.tools
    import hepara.subagents.pdg_agent.agent
    import hepara.subagents.pdg_agent.prompt
    import hepara.subagents.pdg_agent.tools

    importlib.reload(hepara.subagents.mcp_agent.subagents)
    importlib.reload(hepara.subagents.mcp_agent.tools)
    importlib.reload(hepara.subagents.mcp_agent.prompt)
    importlib.reload(hepara.subagents.mcp_agent.agent)
    importlib.reload(hepara.subagents.arxiv_agent.tools)
    importlib.reload(hepara.subagents.faq_agent.tools)
    importlib.reload(hepara.subagents.faq_agent.prompt)
    importlib.reload(hepara.subagents.inspirehep_agent.tools)
    importlib.reload(hepara.subagents.inspirehep_agent.prompt)
    importlib.reload(hepara.subagents.pdg_agent.tools)
    importlib.reload(hepara.subagents.pdg_agent.prompt)
    importlib.reload(hepara.subagents.arxiv_agent.agent)
    importlib.reload(hepara.subagents.faq_agent.agent)
    importlib.reload(hepara.subagents.inspirehep_agent.agent)
    importlib.reload(hepara.subagents.pdg_agent.agent)
    importlib.reload(hepara.prompt)
    root_agent_module = importlib.reload(hepara.agent)
    return root_agent_module.hep_coordinator


async def create_runner(config: dict[str, str]) -> tuple[InMemoryRunner, str]:
    apply_environment(config)
    agent = reload_agent_modules()
    runner = InMemoryRunner(agent=agent, app_name=APP_NAME)
    user_id = config.get("AUTHOR") or "Guest"
    await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id=user_id,
        session_id=SESSION_ID,
    )
    return runner, user_id


def config_signature(config: dict[str, str]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(config.items()))


def ensure_runner(config: dict[str, str]) -> tuple[InMemoryRunner, str]:
    signature = config_signature(config)
    if st.session_state.get("runner_signature") != signature:
        runner, user_id = run_async(create_runner(config))
        st.session_state.runner = runner
        st.session_state.user_id = user_id
        st.session_state.runner_signature = signature
    return st.session_state.runner, st.session_state.user_id


async def get_agent_response(runner: InMemoryRunner, user_id: str, prompt: str) -> str:
    content = Content(role="user", parts=[Part(text=prompt)])
    chunks: list[str] = []

    async for response in runner.run_async(
        user_id=user_id,
        session_id=SESSION_ID,
        new_message=content,
    ):
        if not response.content or not response.content.parts or response.author == "user":
            continue
        for part in response.content.parts:
            if part.text:
                chunks.append(part.text)

    return "\n\n".join(chunks).strip() or "_No response text returned._"


def citation_update_markdown(update: dict[str, Any]) -> str:
    if "Error" in update:
        return f"**Citation update failed:** {update['Error']}"

    result = update.get("Result")
    if isinstance(result, str):
        return result

    return "```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```"


def run_citation_update() -> str:
    apply_environment(current_config())
    import hepara.subagents.inspirehep_agent.tools as inspire_tools

    importlib.reload(inspire_tools)
    update = run_async(inspire_tools.track_citations_updates())
    return citation_update_markdown(update)


def render_sidebar() -> dict[str, str]:
    st.sidebar.header("Configuration")

    with st.sidebar.form("environment_form"):
        google_api_key = st.text_input(
            "GOOGLE_API_KEY",
            value=st.session_state.get("config_GOOGLE_API_KEY", ""),
            type="password",
        )
        author = st.text_input("AUTHOR", value=st.session_state.get("config_AUTHOR", ""))
        categories = st.text_input(
            "CATEGORIES",
            value=st.session_state.get("config_CATEGORIES", ""),
            placeholder="hep-ph, hep-th",
        )
        pdf_path = st.text_input(
            "PDF_PATH",
            value=st.session_state.get("config_PDF_PATH", "./pdf/"),
            placeholder="./pdf/",
        )

        google_model_current = st.session_state.get("config_GOOGLE_MODEL", "gemini-2.5-flash")
        google_choice = st.selectbox(
            "GOOGLE_MODEL",
            GOOGLE_MODEL_OPTIONS + ["Custom"],
            index=option_index(GOOGLE_MODEL_OPTIONS, google_model_current),
        )
        google_custom = st.text_input(
            "Custom GOOGLE_MODEL",
            value="" if google_model_current in GOOGLE_MODEL_OPTIONS else google_model_current,
        )

        ollama_model_current = st.session_state.get("config_OLLAMA_MODEL", "llama3")
        ollama_choice = st.selectbox(
            "OLLAMA_MODEL",
            OLLAMA_MODEL_OPTIONS + ["Custom"],
            index=option_index(OLLAMA_MODEL_OPTIONS, ollama_model_current),
        )
        ollama_custom = st.text_input(
            "Custom OLLAMA_MODEL",
            value="" if ollama_model_current in OLLAMA_MODEL_OPTIONS else ollama_model_current,
        )

        saved = st.form_submit_button("Save configuration", use_container_width=True)

    if saved:
        st.session_state.config_GOOGLE_API_KEY = google_api_key.strip() # type: ignore
        st.session_state.config_AUTHOR = author.strip() # type: ignore
        st.session_state.config_CATEGORIES = categories.strip() # type: ignore
        st.session_state.config_PDF_PATH = pdf_path.strip() or "./pdf/" # type: ignore
        st.session_state.config_GOOGLE_MODEL = model_value(
            GOOGLE_MODEL_OPTIONS,
            google_choice,
            google_custom,
        )
        st.session_state.config_OLLAMA_MODEL = model_value(
            OLLAMA_MODEL_OPTIONS,
            ollama_choice,
            ollama_custom,
        )
        config = current_config()
        save_environment(config)
        apply_environment(config)
        st.session_state.pop("runner_signature", None)
        st.sidebar.success("Configuration saved to .env")

    st.sidebar.divider()
    if st.sidebar.button("Check citation updates", use_container_width=True):
        with st.sidebar.status("Checking citation updates...", expanded=False):
            try:
                st.session_state.citation_update = run_citation_update()
            except Exception as exc:
                st.session_state.citation_update = f"**Citation update failed:** {exc}"

    if st.session_state.get("citation_update"):
        st.sidebar.markdown(st.session_state.citation_update)

    return current_config()


def render_chat_history() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def main() -> None:
    st.set_page_config(page_title="HEPARA", layout="wide")
    load_initial_environment()
    st.session_state.setdefault("messages", [])

    st.title("HEPARA")
    st.caption("High Energy Physics AI Research Assistant")

    config = render_sidebar()
    apply_environment(config)
    runner, user_id = ensure_runner(config)

    render_chat_history()

    prompt = st.chat_input(
        "Ask about papers, citations, particle data, or general HEP questions"
    )
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = run_async(get_agent_response(runner, user_id, prompt))
            except Exception as exc:
                response = f"**Error:** {exc}"
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
