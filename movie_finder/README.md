# Movie Finder

Semantic search over **30 movies** in `movies.json`. Each includes title, director, genre, year, and an original short description.

## Setup and run

Follow the parent [setup instructions](../README.md), including your Pinecone API key. From the repository root:

```powershell
.venv\Scripts\python -m movie_finder
# Optional bonus: retrieval augmented generation (also needs OpenRouter)
.venv\Scripts\python -m movie_finder --rag
```

The app creates the configured serverless Pinecone index if missing, checks dimension/metric, and waits for readiness. An existing index must use **384 dimensions and cosine similarity**. Set another `PINECONE_INDEX` if yours is incompatible. The first run downloads `sentence-transformers/all-MiniLM-L6-v2`; embeddings are computed locally, not by Pinecone.

## Example conversation

Illustrative output; exact ranking and scores must be checked with the downloaded model:

```text
Welcome to Movie Finder! Loading MiniLM and connecting to Pinecone...
Ready! 30 new or changed movies indexed. Type exit to quit.
What would you like to watch? movies by Christopher Nolan
[Up to three matching films are shown with title, director, genre,
year, similarity score, and description.]
What would you like to watch? something scary to watch tonight
[Up to three horror/thriller matches are shown.]
What would you like to watch? a feel-good movie about friendship
[Up to three relevant friendship films are shown.]
What would you like to watch? how to replace a bicycle tire
I couldn't find any matching movies. Try a different genre, director, or theme.
What would you like to watch? exit
Goodbye! Enjoy your next movie.
```

## Retrieval and threshold

Movie metadata is combined into readable text and encoded with MiniLM. Query embeddings use the same model and normalization. Pinecone retrieves the top three vectors by cosine similarity. Each returned result must independently reach **0.35**, configured through `MOVIE_SIMILARITY_THRESHOLD`.

0.35 is an initial precision/recall tradeoff for short, broad movie descriptions: it excludes weak semantic matches while allowing mood/theme requests with different wording. It is a heuristic, not a probability or a guarantee of relevance. Scores depend on the dataset, and an unrelated query may still pass. Validate the three assignment examples plus unrelated queries before submission; adjust this value if measured results justify it. Lower values increase recall and false positives; higher values reduce false positives but may miss vague requests. Fewer than three results are shown when fewer qualify. There is no LLM call if nothing passes.

## One-time indexing and updates

Every movie's stable ID is a SHA-256 digest of its title and year. On startup, the app fetches those IDs and compares stored content hashes with the current metadata. Only new or edited movies are embedded and upserted; an unchanged restart performs no embedding/upsert work. Upserting stable IDs replaces existing vectors instead of adding duplicates. Fetch polling allows for eventual consistency after writes.

Use a namespace dedicated to this dataset/model (`movies-minilm-v1` by default). Renaming a movie or changing its year creates a new identity; deleted/renamed source records are not automatically removed from Pinecone. This avoids accidental destructive cleanup. For a different dataset or embedding model, use a fresh namespace/index.

## Optional RAG bonus

`--rag` sends the query and retrieved, threshold-qualified metadata to OpenRouter, with instructions to recommend only those films and avoid inventing facts. Original search results remain visible even if the LLM request fails. The Streamlit movie page has the same feature behind a toggle.

## Live acceptance checklist

1. Run the app twice; the second unchanged run should report zero new/changed movies.
2. Check the Pinecone namespace contains exactly 30 records after the first run.
3. Test all three assignment queries and inspect titles, ranks, and scores.
4. Test unrelated queries and verify the no-match response; record any threshold adjustment and its rationale.
5. Run `--rag` and ensure recommendations only mention retrieved films.
6. Type `exit` and test blank queries and invalid credentials.
