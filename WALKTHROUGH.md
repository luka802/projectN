# How to explain the project

## TravelBuddy in one minute

`TravelBuddy` stores confirmed choices, conversation history, and whether the conversation has ended. There are three steps: trip type, accommodation, and activity. The options at the last step depend on the trip type, so a mountain trip cannot accidentally finish with snorkeling.

An exact button label or number is accepted immediately. A natural-language preference is sent to OpenRouter with the conversation history and the current valid choices. The model returns a JSON choice; the app validates and normalizes it before updating state. Unexpected answers and failed requests leave confirmed choices intact. `exit` is handled locally.

Back navigation removes the latest choice. Editing an earlier step clears that step and its dependents: changing the setting requires choosing the stay and activity again.

## Movie Finder in one minute

1. Load the 30 records in `movies.json` and validate their fields.
2. Give each film a stable ID derived from title and year, and compare its content hash with Pinecone.
3. Embed only new or edited metadata with local `all-MiniLM-L6-v2` (384 dimensions), then upsert under the stable IDs. Repeated startup does not add duplicates.
4. Embed the user's query with the same model. Ask Pinecone for the three nearest vectors using cosine similarity. Explicit director requests also constrain director metadata.
5. Show only matches at or above 0.30. If none qualify, say there are no matching films.

The threshold was chosen using measured relevant and unrelated queries, documented in the Movie Finder README. Similarity is not a review score or a probability.

## What makes the optional feature RAG?

Retrieval supplies qualifying films from Pinecone. Generation sends only those retrieved film facts and the request to OpenRouter to produce recommendations. The system prompt tells it not to invent films or facts. Search results remain available if generation fails. This is retrieval augmented generation, rather than asking an LLM to guess films from memory.

## Where the speed comes from

- The Streamlit resource cache reuses the model and database client.
- Exact travel choices skip an unnecessary network call.
- A bounded five-minute query cache avoids repeating embedding and Pinecone retrieval for identical requests, and returns independent copies.
- Saved films, itinerary choices, and displayed recommendations use per-session state, so routine button clicks do not repeat expensive work.
- Local fonts remove external font-loading requests.

## Useful files to open during a review

- `travel_buddy/bot.py`: state transitions, model interpretation, and recovery.
- `movie_finder/search.py`: ingestion, embeddings, Pinecone retrieval, caching, and RAG.
- `common/llm.py`: OpenRouter authentication, timeouts, and fallback handling.
- `web_app.py` and `ui_helpers.py`: interface and saved-film/export behavior.
- `tests/`, `VALIDATION.md`, and GitHub Actions: regression checks and observed live results.

The web interface is an optional companion. Both original console entry points still work independently.
