# Weekend & Watchlist

[![Windows and Linux checks](https://github.com/luka802/projectN/actions/workflows/checks.yml/badge.svg)](https://github.com/luka802/projectN/actions/workflows/checks.yml)

Two Python console assignments with both optional bonuses: grounded LLM movie recommendations (RAG) and a Streamlit interface for both apps.

## Quick start

Use **Python 3.12**, the version verified locally and in GitHub Actions. Open a terminal in this directory:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

On macOS/Linux use `python3 -m venv .venv`, `.venv/bin/python`, and `cp .env.example .env` instead. No shell activation is required.

`requirements-lock.txt` records the exact dependency versions installed during local verification on Windows/Python 3.12. Use `pip install -r requirements-lock.txt` to reproduce that environment; `requirements.txt` keeps the supported version ranges readable.

Open `.env` in a text editor and fill in `OPENROUTER_API_KEY` and `PINECONE_API_KEY`. Never commit this file. Create keys at [OpenRouter](https://openrouter.ai/keys) and [Pinecone](https://app.pinecone.io/). The configured Pinecone project must allow creating a serverless index. Defaults are AWS `us-east-1`, 384 dimensions, cosine metric. Check your provider account's current limits before running.

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
assets/            Cinema and coastal styles, plus original SVG illustrations
static/art/        Eight original local cinema and destination images
static/fonts/      Locally served fonts and open licenses
.streamlit/        Theme and lightweight runtime settings
.github/workflows/ Windows and Linux offline regression checks
requirements.txt   Dependency constraints
.env.example       Safe configuration template
```

Read [TravelBuddy's README](travel_buddy/README.md) and [Movie Finder's README](movie_finder/README.md) for conversations and design decisions.

[WALKTHROUGH.md](WALKTHROUGH.md) explains the code paths and design choices for a short project review.

## Verification

```powershell
.venv\Scripts\python -m unittest discover -s tests -v
```

For a lightweight test-only environment, install `requirements-test.txt` instead of the full requirements. `requirements.txt` is for running the apps; `requirements-lock.txt` reproduces the verified Windows environment. These dependency files are not user documents or exported itineraries.

These tests do not use API keys. Separate live OpenRouter and Pinecone checks, actual retrieval scores, and UI checks are recorded in [VALIDATION.md](VALIDATION.md). The acceptance checklists in each app's README can be repeated with your configured accounts. Do not include `.env`, `.venv`, or downloaded model weights in the repository.

## Dependencies and API choices

The Pinecone SDK is constrained to version 7 to use its documented `Pinecone`, `ServerlessSpec`, `Index.fetch`, `upsert`, and `query` interfaces consistently. MiniLM embeddings run locally; Pinecone stores/searches them. OpenRouter receives travel conversation history and, in RAG mode, only the query and retrieved movie metadata. No travel conversation is saved to disk.

References: [OpenRouter API](https://openrouter.ai/docs/api/reference/overview), [Pinecone Python SDK](https://github.com/pinecone-io/pinecone-python-client/tree/v7.3.0), [MiniLM model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), [Streamlit](https://docs.streamlit.io/).

## Using the website

The default page is **Find a film**. Use the top navigation to switch between all three sections:

| Page | What to do | What stays in this session |
| --- | --- | --- |
| Plan a getaway | Choose a setting, stay, and activity; or type a preference and select **Continue** | Confirmed choices and conversation history |
| Find a film | Enter a mood, genre, or director, or choose an example; use **Help me choose** for an AI recommendation | Latest results, recommendation, and saved selections |
| Saved films | Review your shortlist, remove films, or download it | Films saved across searches |

**Plan a getaway** uses the selected Coastal Escape theme: ocean blue, white panels, destination photographs, and pale choice buttons. Clicking a choice advances immediately. **Back a step** removes the latest choice. On the completed plan, **Change setting**, **Change stay**, and **Change activity** clear the edited step and any later choices. **Save your weekend plan** downloads a text itinerary; it does not book accommodation or activities.

**Find a film** and **Saved films** use the Movie Lounge theme: charcoal, restrained amber accents, a cosy movie-night backdrop, and compact landscape film cards. The initial featured collection appears without loading the model or connecting to Pinecone. A submitted search uses real MiniLM embeddings and Pinecone. Six mood shortcuts run actual searches. **More like this** searches using a result’s genre and description; **More to explore** offers six collection-based search shortcuts. **Save these picks** exports the current results; **Download saved films** exports the separate shortlist you built across searches. Search failures retain previous results. A successful new search clears the old AI recommendation.

Trip choices and saved films are held in Streamlit Session State, not an account or permanent database. Switching pages in the app preserves them; reloading, closing, or reconnecting the browser can start a new session. Download anything you want to keep.

## Configuration and service requirements

| Feature | Required service |
| --- | --- |
| Featured films, saving featured films, exact travel choices | No API request |
| Natural-language travel preferences | OpenRouter |
| Submitted movie searches | Pinecone and local MiniLM weights |
| AI movie recommendations | Movie retrieval plus OpenRouter |

The environment template contains these defaults:

| Variable | Purpose / default |
| --- | --- |
| `OPENROUTER_API_KEY` | Your OpenRouter key |
| `OPENROUTER_MODEL` | Primary model: `meta-llama/llama-3-8b-instruct` |
| `OPENROUTER_FALLBACK_MODEL` | Fallback model: `openrouter/free` |
| `PINECONE_API_KEY` | Key for the intended Pinecone project |
| `PINECONE_INDEX` | Index name: `movie-finder` |
| `PINECONE_NAMESPACE` | Dataset namespace: `movies-minilm-v1` |
| `PINECONE_CLOUD` / `PINECONE_REGION` | New-index location: `aws` / `us-east-1` |
| `MOVIE_SIMILARITY_THRESHOLD` | Minimum cosine score: `0.30` |

Model availability and account quotas can change. The client tries the configured fallback after supported provider errors, network failures, and empty or malformed primary responses. It reports a readable error if both attempts fail.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Missing API key | Put the relevant key in the root `.env`, then restart the app |
| OpenRouter error | Check the key, configured model IDs, connection, and account limits; retrieved films remain available if recommendation fails |
| Pinecone dimension/metric error | Use a 384-dimensional cosine index, or choose a new `PINECONE_INDEX` |
| First movie search is slow | Allow the initial model download and index setup to finish; later searches reuse the loaded resources |
| No matching movies | Try a different mood, genre, or director; the collection contains 30 films and only qualifying results are shown |
| Port 8501 is busy | Stop the previous server, or add `--server.port 8502` to the Streamlit command |
| Code changes do not appear | Restart Streamlit; the source watcher is intentionally disabled to avoid transformer-module scanning |

## Performance and design notes

The Streamlit resource cache reuses the model and database client. Identical movie searches are cached for up to five minutes (32 entries maximum). Cached results are copied, respect the threshold, and clear when ingestion updates the collection. Exact travel choices skip the LLM. [RESEARCH.md](RESEARCH.md) records comparable-product research and observed backend timings.

All eight raster images and all fonts are served locally. Original artwork, source paths, and generation prompts are recorded in [ARTWORK.md](ARTWORK.md). The six-panel genre atlas supplies artwork for films without an individual image. Artwork is illustrative, not an official movie poster or a claim of a bookable destination.

User/provider content is HTML-escaped before insertion into styled cards. The interface includes keyboard focus indicators, reduced-motion styles, and responsive card layouts. Automated UI tests check behavior; observed live checks and the limits of visual verification are recorded in [VALIDATION.md](VALIDATION.md).

GitHub Actions runs the offline tests on Windows and Linux with Python 3.12. It uses `requirements-test.txt`, which omits large model dependencies because tests inject service doubles. Live checks require the full requirements and configured accounts.
