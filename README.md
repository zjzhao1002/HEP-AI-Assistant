# HEPARA: High Energy Physics AI Research Assistant

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Framework](https://img.shields.io/badge/framework-google--adk-orange.svg)](https://github.com/google/adk)
[![Model](https://img.shields.io/badge/model-gemini--2.5--flash-purple.svg)](https://deepmind.google/technologies/gemini/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**HEPARA** (High Energy Physics AI Research Assistant) is a specialized research companion designed for physicists working in High Energy Physics. Built on the **Google Agent Development Kit (ADK)** and powered by **Gemini 2.5 Flash**, HEPARA automates the tedious parts of literature tracking and citation monitoring.

---

## 🚀 Features

-   **📊 Citation Tracking:** Monitor your own citation counts and get notified of new citations automatically using INSPIRE-HEP data.
-   **📑 arXiv Monitoring:** Stay up-to-date with the latest papers in specific HEP categories (e.g., hep-ph, hep-th).
-   **🔍 Trend Discovery:** Identify trending research topics and keywords in recent publications.
-   **💡 Intelligent Recommendations:** Get personalized paper recommendations based on your research interests and keywords.
-   **🤖 Multi-Agent Architecture:** Powered by a coordinator agent that orchestrates specialized sub-agents for different research tasks.

## 🛠️ Tech Stack

-   **Core:** [Google Agent Development Kit (ADK)](https://github.com/google/adk)
-   **Model:** Google Gemini 2.5 Flash
-   **Package Manager:** [uv](https://github.com/astral-sh/uv)
-   **Data Sources:** INSPIRE-HEP API, arXiv API

---

## ⚙️ Installation

### Prerequisites

-   Python 3.13 or higher
-   [uv](https://github.com/astral-sh/uv) installed
-   A Google Gemini API Key

### Setup

1.  **Clone the repository:**
    \`\`\`bash
    git clone https://github.com/your-username/HEP-AI-Assistant.git
    cd HEP-AI-Assistant
    \`\`\`

2.  **Sync dependencies:**
    \`\`\`bash
    uv sync
    \`\`\`

3.  **Configure environment variables:**
    Create a \`.env\` file in the root directory:
    \`\`\`env
    # Gemini API Key
    GOOGLE_API_KEY=your_api_key_here

    # User Configuration
    AUTHOR="Your Name"
    CATEGORIES="hep-ph, hep-th"
    OLLAMA_MODEL="llama3" # Used for keyword extraction via arXivFlow
    \`\`\`

---

## 🏃 Usage

Launch the interactive assistant:

\`\`\`bash
uv run main.py
\`\`\`

Upon startup, HEPARA will:
1.  Initialize your research session.
2.  Automatically check for new citations for the configured \`AUTHOR\`.
3.  Ready itself for your questions about recent papers, trends, or literature searches.

### Example Queries

-   *"What are the trending topics in hep-ph this week?"*
-   *"Can you recommend some papers on 'Dark Matter'?"*
-   *"Have I received any new citations recently?"*

---

## 📁 Project Structure

```bash
├── hepara/
│   ├── agent.py           # Root Coordinator Agent
│   ├── subagents/
│   │   ├── arxiv_tracker/ # arXiv monitoring and recommendations
│   │   └── citations_tracker/ # INSPIRE-HEP citation tracking
├── main.py                # Entry point (CLI)
├── pyproject.toml         # Dependencies and project metadata
└── README.md              # This file
```

---

## 🤝 Contributing

Contributions are welcome! Whether it's adding new sub-agents for different data sources or improving the prompts, please feel free to open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
