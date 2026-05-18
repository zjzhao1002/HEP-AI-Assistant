# HEPARA: High Energy Physics AI Research Assistant

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Framework](https://img.shields.io/badge/framework-google--adk-orange.svg)](https://github.com/google/adk)
[![Model](https://img.shields.io/badge/model-gemini--2.5--flash-purple.svg)](https://deepmind.google/technologies/gemini/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**HEPARA** (High Energy Physics AI Research Assistant) is a specialized research companion designed for physicists working in High Energy Physics. Built on the **Google Agent Development Kit (ADK)** and powered by **Gemini 2.5 Flash**, HEPARA automates literature tracking, citation monitoring, and trend analysis.

---

## 🚀 Features

-   **📊 Citation Monitoring & Analysis:** 
    -   Track your own citation counts and get notified of new citations or publications via `track_citations_updates`.
    -   Fetch detailed citation metrics for any author on INSPIRE-HEP.
    -   Analyze citation graphs: explore what a paper cites (references) or what papers cite it.
-   **📑 arXiv Intelligence:**
    -   Search for papers on arXiv with advanced query support.
    -   **PDF Downloading:** Directly download paper PDFs to your local machine.
    -   **Trending Recommendations:** Discover the latest papers based on trending topics in your field (powered by `arxivflow`).
-   **🤖 Intelligent Coordination:** A root agent orchestrates specialized sub-agents (`arxiv_agent`, `inspirehep_agent`) to provide seamless answers to complex research queries.
-   **🛡️ Robust Reliability:** Enterprise-grade rate limiting and connection pooling for arXiv/INSPIRE-HEP ensures consistent operation without IP blocking.

## 🛠️ Tech Stack

-   **Framework:** [Google Agent Development Kit (ADK)](https://github.com/google/adk)
-   **Model:** Google Gemini 2.5 Flash
-   **Keyword Extraction:** [arXivFlow](https://github.com/zjzhao1002/arxivflow) (requires Ollama)
-   **Data Sources:** INSPIRE-HEP API, arXiv API
-   **Environment:** Python 3.13+, [uv](https://github.com/astral-sh/uv)

---

## ⚙️ Installation

### Prerequisites

-   Python 3.13 or higher
-   [uv](https://github.com/astral-sh/uv) installed
-   A Google Gemini API Key

### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/HEP-AI-Assistant.git
    cd HEP-AI-Assistant
    ```

2.  **Sync dependencies:**
    ```bash
    uv sync
    ```

3.  **Configure environment variables:**
    Create a `.env` file in the root directory:
    ```env
    # Gemini API Key
    GOOGLE_API_KEY=your_api_key_here

    # User Configuration
    AUTHOR="your name" # To get accurate results, the INSPIRE-HEP author identifier is recommended. 
                       # It should be something like Joe.Smith.1 
    CATEGORIES="hep-ph, hep-th" # The arXiv categories you are interested in
    OLLAMA_MODEL="llama3" # Used for keyword extraction via arXivFlow
    ```

---

## 🏃 Usage

Launch the interactive assistant:

```bash
uv run main.py
```

Upon startup, HEPARA will:
1.  Initialize your research session.
2.  Automatically check for new citations for the configured \`AUTHOR\`.
3.  Ready itself for your questions about recent papers, trends, or literature searches.

### Example Queries

-   *"What are the trending topics in hep-ph this week?"*
-   *"Download the PDF for arXiv:2301.00001"*
-   *"Who is citing my latest paper?"*
-   *"Find papers on 'Dark Matter' published in the last month."*

---

## 📁 Project Structure

```bash
├── hepara/
│   ├── agent.py           # Root Coordinator Agent
│   ├── subagents/
│   │   ├── arxiv_agent/       # arXiv search, PDF download, and trends
│   │   └── inspirehep_agent/  # INSPIRE-HEP citation tracking and graph analysis
├── main.py                # Entry point (CLI)
├── pyproject.toml         # Dependencies and project metadata
├── README.md              # This file
└── GEMINI.md              # Project internal documentation
```

---

## 🤝 Contributing

Contributions are welcome! Whether it's adding new sub-agents for different data sources or improving the prompts, please feel free to open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
