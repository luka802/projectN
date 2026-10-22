# Validation record

Verified locally on Windows with Python 3.12 on October 22, 2026.

## Automated checks

`python -m unittest discover -s tests -v`: **25 tests passed** after the research and performance update.

Coverage includes travel state/history, unexpected and malformed answers, service failures, exit handling, unchanged/revised indexing, director filtering, threshold boundaries, Pinecone year normalization, RAG context, and OpenRouter fallback.

Streamlit's `AppTest` verifies the full guided travel flow, back/reset controls, itinerary download availability, one-click search suggestions, preserved results/recommendations across navigation, on-demand RAG without rerunning retrieval, recovery after search failure, and clearing outdated recommendations on new searches. A separate unit test confirms exact menu selections do not wait for an LLM request and back navigation preserves conversation context.

## Live Pinecone and MiniLM

The first live sync uploaded 30 movie records. An immediate unchanged sync uploaded **0** records. The application used real local `all-MiniLM-L6-v2` embeddings and a Pinecone 384-dimensional cosine index.

| Query | Retrieved films and cosine scores |
| --- | --- |
| something scary to watch tonight | The Conjuring 0.403; A Quiet Place 0.380; Get Out 0.313 |
| movies by Christopher Nolan | Interstellar 0.623; Inception 0.582; Memento 0.540 |
| a feel-good movie about friendship | The Shawshank Redemption 0.511; The Intouchables 0.479; Paddington 2 0.458 |
| how to replace a bicycle tire | No matching movies above the 0.30 threshold |

Explicit director filtering kept every Nolan result attributed to Christopher Nolan. Separate local calibration queries about tax filing and cake recipes also remained below the threshold.

## Live OpenRouter

- A connection request completed successfully.
- RAG returned recommendations for only the three retrieved friendship movies and acknowledged the darker setting of The Shawshank Redemption.
- TravelBuddy completed Mountains → Cozy guesthouse → Stargazing.
- The unexpected accommodation answer "I want to stay on the Moon" repeated the accommodation menu without advancing.
- The natural-language answer "look at the stars" selected Stargazing.
- `exit` returned a goodbye and closed the conversation.

Live outputs can vary with model availability, provider limits, and stochastic LLM behavior. These are observed checks, not a guarantee of every possible query. Credentials and local configuration are excluded from Git.

## Research and performance follow-up

- Saved-film selection, removal, copying, export, and navigation persistence are covered by provider-free tests.
- Direct itinerary editing clears later choices; changing Mountains to Beach cannot leave a mountain activity selected.
- Repeated queries skip embedding and Pinecone work, return independent copies, expire after five minutes, and honor threshold changes.
- A live unknown-director query (Steven Spielberg, absent from the collection) returned no matches; the surname query "movies by nolan" returned only Nolan films.
- A later live natural-language trip preference completed correctly in 3.84 seconds. The model response budget was retained after an attempted reduction proved unreliable in a separate check.
- Both local font URLs returned HTTP 200 with valid font bytes. Core text/button contrast pairs ranged from 4.61:1 to 11.27:1.
- Ctrl+C during model/search calls returns a clean goodbye in the console regression checks.
- [RESEARCH.md](RESEARCH.md) and `performance.json` record methods and backend timings.
- The GitHub Actions run for commit `64ae006` passed all offline checks in clean Windows and Linux environments.
