# Validation record

Verified locally on Windows with Python 3.12 on October 22, 2026.

## Automated checks

`python -m unittest discover -s tests -v`: **17 tests passed** after the interface update.

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
