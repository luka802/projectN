# UX and performance notes

Reviewed official product pages and framework documentation on October 22, 2026. These are adaptations to this small assignment, not copies of another site's design.

| Reference | Useful pattern | Application here |
| --- | --- | --- |
| [Letterboxd watchlists](https://support.letterboxd.com/hc/en-us/articles/15179261056143-What-s-the-difference-between-my-lists-and-my-watchlist) | Add/remove films directly while discovering them | Save individual results to a session shortlist, remove them, and download the combined list across searches |
| [Wanderlog](https://wanderlog.com/) | Keep a trip's information organized in one itinerary | Directly edit the setting, stay, or activity from the completed itinerary; changing an earlier step clears dependent choices |
| [JustWatch](https://www.justwatch.com/) | A unified watchlist helps retain discoveries | Keep the shortlist separate from the latest search results so a new query does not erase saved films |
| [Streamlit caching](https://docs.streamlit.io/develop/concepts/architecture/caching) | Share expensive resources; keep personal state in Session State | Reuse the model/database client and briefly cache public search results; keep each user's saved films and itinerary in their own session |
| [Streamlit static files](https://docs.streamlit.io/develop/concepts/configuration/serving-static-files) | Serve small supporting assets locally | Bundle the two fonts and their OFL licenses instead of requesting Google Fonts during page rendering |

## Measured speed

One local run using real MiniLM, Pinecone, and OpenRouter measured:

| Operation | Observed time |
| --- | --- |
| Cold model/client initialization | 12.13 seconds |
| First query after initialization | 0.839 seconds |
| Repeated identical query from cache | Less than 0.001 seconds |
| Exact travel choice in the backend | Less than 0.001 seconds |
| Natural-language travel preference through OpenRouter | 3.84 seconds |

These measure backend operations, not complete browser rendering, and vary by machine/network/provider load. The first model download is excluded. Raw measurements are in `performance.json`.

The query cache is bounded to 32 entries per finder, expires after five minutes, returns copies to prevent accidental mutation, and clears on ingestion changes. It does not cache AI recommendations. The model remains local; fresh retrieval still uses Pinecone.

## Scope choices

The assignment's two Python console apps and all required steps remain intact. There are no invented streaming-provider claims, live hotel availability, bookings, ratings, or maps: the supplied movie metadata and three-choice travel flow do not support those features. The interface explains its small collection and offers recovery suggestions when no movie qualifies.

Fonts are the original Manrope and DM Sans files from [Google Fonts](https://github.com/google/fonts), with their unmodified OFL licenses under `static/fonts/`.
