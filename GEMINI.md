# Project Overview
HEP-AI-Assistant is a research assistant specialized in High Energy Physics (HEP). It is built using the `google-adk` framework and leverages Gemini models (e.g., `gemini-2.5-flash`) to answer user questions, track citations, and monitor arXiv trends.

## Technologies
- **Language:** Python 3.13+
- **Framework:** `google-adk` (Google Agent Development Kit)
- **Model:** Gemini 2.5 Flash
- **Key Libraries:** `arxivflow` (keyword extraction), `pandas` (data handling), `httpx` (API requests), `python-dotenv`
- **Environment Management:** `uv`

# Building and Running
The project uses `uv` for dependency management.

## Installation
```bash
uv sync
```

## Running the Assistant
The entry point for the application is `main.py`. It runs the agent in an `InMemoryRunner`.
```bash
uv run main.py
```

## Configuration
The project uses a `.env` file for environment variables:
- `GOOGLE_API_KEY`: Required for Gemini.
- `AUTHOR`: The INSPIRE-HEP author identifier (e.g., `Joe.Smith.1`).
- `CATEGORIES`: Comma-separated arXiv categories (e.g., `hep-ph, hep-th`).
- `OLLAMA_MODEL`: Required for keyword extraction via `arxivflow` (e.g., `llama3`).

# Architecture
- `main.py`: The entry point that initializes the environment and runs the `hep_coordinator`.
- `hepara/agent.py`: Defines the `hep_coordinator` (root agent) which orchestrates sub-agents.
- `hepara/subagents/`: Contains specialized agents:
    - `arxiv_agent`: 
        - `search_papers`: Searches arXiv via Atom API.
        - `download_pdf`: Downloads PDFs from arXiv.
        - `recommend_by_trends`: Recommends papers based on trending keywords (uses `arxivflow`).
    - `inspirehep_agent`: 
        - `search_papers`: Searches INSPIRE-HEP literature.
        - `get_paper_citations`: Analyzes citation graphs (citing/cited by).
        - `get_author_citations`: Fetches author-specific citation metrics.
        - `track_citations_updates`: Monitors changes in author citations since last check.

# Development Conventions
- **Agent Definition:** New agents or modifications to existing ones should be done in `hepara/agent.py` or within `hepara/subagents/`.
- **Framework Usage:** Follow `google-adk` patterns for agent creation and tool integration.
- **Asynchronous Code:** Use `asyncio` for running agents and handling tool calls. All API-interacting tools are asynchronous.
- **Network & Rate Limiting:** 
    - **Shared Client:** Use a shared `httpx.AsyncClient` for sub-agents (e.g., `_get_arxiv_client` in `arxiv_agent/tools.py`) to enable connection pooling and improve performance.
    - **Sequential Access:** Strictly adhere to provider rate limits. For arXiv, use a global `asyncio.Semaphore(1)` and a minimum 3-second request interval (`MIN_REQUEST_INTERVAL`) to prevent IP blocking.
    - **Retry Logic:** Implement robust retry handling for `429` (Rate Limited) and `503` (Service Unavailable) errors, ensuring timing state is updated after pauses.

# License
This project is licensed under the MIT License. See the `LICENSE` file for full details.
