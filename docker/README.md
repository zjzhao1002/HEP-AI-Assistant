# HEPARA Docker Image Overview

HEPARA is a High Energy Physics AI Research Assistant that helps researchers search papers, track citations, recommend recent arXiv papers, and download PDFs. This Docker image packages the local Streamlit app together with Ollama, so users can run the assistant locally with one container.

Source code and documentation are available in the GitHub repository: [zjzhao1002/HEP-AI-Assistant](https://github.com/zjzhao1002/HEP-AI-Assistant).

The image includes:

-   The HEPARA Streamlit web app
-   Python dependencies managed by `uv`
-   Ollama for local keyword extraction and trend recommendations
-   Persistent storage support for user configuration, citation records, downloaded PDFs, and Ollama models

## Quick Start

Pull the image:

```bash
docker pull zjzhao1002/hepara:latest
```

Run the app:

```bash
docker run --rm -p 8501:8501 -p 11434:11434 \
  -v hepara-data:/app/data \
  -v hepara-ollama:/root/.ollama \
  zjzhao1002/hepara:latest
```

Open the app at:

```text
http://localhost:8501
```

In the Streamlit sidebar, enter your `GOOGLE_API_KEY`, `AUTHOR`, `CATEGORIES`, and model settings, then click **Save configuration**.

## Persistent Data

The container uses two recommended Docker volumes:

-   `hepara-data`: stores saved configuration, citation records, and downloaded PDFs.
-   `hepara-ollama`: stores downloaded Ollama models.

Downloaded PDFs are saved inside the container at:

```text
/app/data/pdf
```

The saved Streamlit configuration is persisted through:

```text
/app/data/.env
```

Citation tracking records are also stored under `/app/data`, so citation updates remain available after restarting the container.

## Ollama Model

By default, the container uses:

```text
llama3
```

On first startup, the container starts Ollama and pulls the configured model if it is not already available in the `hepara-ollama` volume. This can take a while depending on the model size and network speed.

To use a different Ollama model:

```bash
docker run --rm -p 8501:8501 -p 11434:11434 \
  -v hepara-data:/app/data \
  -v hepara-ollama:/root/.ollama \
  -e OLLAMA_MODEL=qwen2.5 \
  zjzhao1002/hepara:latest
```

## Required Configuration

Most users should configure these values from the Streamlit sidebar:

-   `GOOGLE_API_KEY`: Google Gemini API key
-   `AUTHOR`: author name or INSPIRE-HEP author identifier
-   `CATEGORIES`: arXiv categories of interest, such as `hep-ph, hep-th`
-   `GOOGLE_MODEL`: Gemini model for the main assistant
-   `OLLAMA_MODEL`: Ollama model for local arXivFlow keyword extraction

The local Docker app sets:

```text
ARXIVFLOW_KEYWORD_BACKEND=ollama
PDF_PATH=/app/data/pdf
```

## Ports

The container exposes:

-   `8501`: Streamlit web app
-   `11434`: Ollama API

## Notes

-   The image is intended for local use.
-   The first run may be slower because Ollama needs to download the selected model.
-   Keep the recommended volumes if you want saved configuration, citation history, PDFs, and Ollama models to survive container restarts.
-   The container runs Ollama and Streamlit together for convenience.
