# Weekend & Watchlist

Two Python console assignments with both optional bonuses: grounded LLM movie recommendations (RAG) and a Streamlit interface for both apps.

## Quick start

Use Python **3.11 or 3.12**. Open a terminal in this directory:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

On macOS/Linux use `python3 -m venv .venv`, `.venv/bin/python`, and `cp .env.example .env` instead. No shell activation is required.

`requirements-lock.txt` records the exact dependency versions installed during local verification on Windows/Python 3.12. Use `pip install -r requirements-lock.txt` to reproduce that environment; `requirements.txt` keeps the supported version ranges readable.

Edit `.env` locally and fill in `OPENROUTER_API_KEY` and `PINECONE_API_KEY`. Never commit this file. Create keys at [OpenRouter](https://openrouter.ai/keys) and [Pinecone](https://app.pinecone.io/). The configured Pinecone project must allow creating a serverless index. Defaults are AWS `us-east-1`, 384 dimensions, cosine metric. Check your provider account's current limits before running.

```powershell
.venv\Scripts\python -m travel_buddy
.venv\Scripts\python -m movie_finder
.venv\Scripts\python -m movie_finder --rag
.venv\Scripts\python -m streamlit run web_app.py
```

All commands above run **from this directory**. The web app normally opens at `http://localhost:8501`. Console programs support `exit` at any prompt and Ctrl+C. The first movie search downloads the MiniLM model to the ignored `.model-cache` folder and creates/synchronizes the Pinecone index; allow extra time and an internet connection. An existing `HF_HOME` environment setting takes precedence.

## Project structure

```text
common/            OpenRouter client and local environment loading
travel_buddy/      Travel chatbot, state, history, console entry point, README
movie_finder/      Movie data, ingestion, retrieval, RAG, console entry point, README
tests/             Offline regression tests using service doubles
web_app.py         Optional Streamlit UI for both apps
requirements.txt   Dependency constraints
.env.example       Safe configuration template
```

Read [TravelBuddy's README](travel_buddy/README.md) and [Movie Finder's README](movie_finder/README.md) for conversations and design decisions.

## Verification

```powershell
.venv\Scripts\python -m unittest discover -s tests -v
```

These tests do not use API keys or claim to validate live services. Before submitting, run the live acceptance checklist in each app's README with your configured accounts. Do not include `.env`, `.venv`, or downloaded model weights in the repository.

## Dependencies and API choices

The Pinecone SDK is constrained to version 7 to use its documented `Pinecone`, `ServerlessSpec`, `Index.fetch`, `upsert`, and `query` interfaces consistently. MiniLM embeddings run locally; Pinecone stores/searches them. OpenRouter receives travel conversation history and, in RAG mode, only the query and retrieved movie metadata. No travel conversation is saved to disk.

References: [OpenRouter API](https://openrouter.ai/docs/api/reference/overview), [Pinecone Python SDK](https://github.com/pinecone-io/pinecone-python-client/tree/v7.3.0), [MiniLM model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), [Streamlit](https://docs.streamlit.io/).
