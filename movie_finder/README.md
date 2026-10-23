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

Abridged results from the live acceptance run (scores rounded to three decimals; the full console output also includes genre and description):

```text
Welcome to Movie Finder! Loading MiniLM and connecting to Pinecone...
Ready! 30 new or changed movies indexed. Type exit to quit.
What would you like to watch? movies by Christopher Nolan
1. Interstellar (2014) | Christopher Nolan | similarity 0.623
2. Inception (2010) | Christopher Nolan | similarity 0.582
3. Memento (2000) | Christopher Nolan | similarity 0.540
What would you like to watch? something scary to watch tonight
1. The Conjuring (2013) | similarity 0.403
2. A Quiet Place (2018) | similarity 0.380
3. Get Out (2017) | similarity 0.313
What would you like to watch? a feel-good movie about friendship
1. The Shawshank Redemption (1994) | similarity 0.511
2. The Intouchables (2011) | similarity 0.479
3. Paddington 2 (2017) | similarity 0.458
What would you like to watch? how to replace a bicycle tire
I couldn't find any matching movies. Try a different genre, director, or theme.
What would you like to watch? exit
Goodbye! Enjoy your next movie.
```

## Retrieval and threshold

Movie metadata is combined into readable text and encoded with MiniLM. Query embeddings use the same model and normalization. Explicit requests such as "movies by Christopher Nolan" also apply a Pinecone director metadata filter, so semantic similarity cannot substitute a film by another director. The filter recognizes full director names and unambiguous surnames in explicit "by" requests. An unknown explicit director produces no matches rather than unrelated recommendations. Other wording still uses semantic search. Pinecone retrieves the top three vectors by cosine similarity. Each returned result must independently reach **0.30**, configured through `MOVIE_SIMILARITY_THRESHOLD`.

0.30 was selected after measuring real MiniLM cosine scores over this dataset. The scary-movie query returned The Conjuring (0.403), A Quiet Place (0.380), and Get Out (0.313). The friendship query returned The Shawshank Redemption (0.511), The Intouchables (0.479), and Paddington 2 (0.458). Three unrelated queries about bicycle repair, tax filing, and cake recipes had maximum scores of 0.133, 0.049, and 0.124 respectively. Thus 0.30 keeps the three horror matches while rejecting these unrelated examples. It is a heuristic, not a probability or a guarantee of relevance. Scores depend on the dataset, and an unrelated query may still pass. Validate the three assignment examples plus unrelated queries before submission; adjust this value if measured results justify it. Lower values increase recall and false positives; higher values reduce false positives but may miss vague requests. Fewer than three results are shown when fewer qualify. There is no LLM call if nothing passes.

## One-time indexing and updates

Every movie's stable ID is a SHA-256 digest of its title and year. On startup, the app fetches those IDs and compares stored content hashes with the current metadata. Only new or edited movies are embedded and upserted; an unchanged restart performs no embedding/upsert work. Upserting stable IDs replaces existing vectors instead of adding duplicates. Fetch polling allows for eventual consistency after writes.

Use a namespace dedicated to this dataset/model (`movies-minilm-v1` by default). Renaming a movie or changing its year creates a new identity; deleted/renamed source records are not automatically removed from Pinecone. This avoids accidental destructive cleanup. For a different dataset or embedding model, use a fresh namespace/index.

## Optional RAG bonus

`--rag` sends the query and retrieved, threshold-qualified metadata to OpenRouter, with instructions to recommend only those films and avoid inventing facts. Original search results remain visible even if the LLM request fails. The Streamlit movie page offers the same feature through **Help me choose**, without repeating retrieval. Results and recommendations persist across page navigation. **Save these picks** downloads a text watchlist.

## Faster repeat searches and saved films

Identical queries are cached for five minutes (up to 32 entries), with independent result copies and cache invalidation on changed ingestion. The web UI also lets you save individual films across searches in **Saved for later** and download that combined shortlist. The dedicated **Saved films** page offers the same shortlist and removal controls. **Download saved films** exports `saved-films.txt`; **Save these picks** exports the current search results as `my-watchlist.txt`. These lists can differ because saved films span multiple searches.

Saved selections last for the Streamlit session; a browser reload or disconnection can reset them. Download your shortlist to keep it. The three initial featured films are collection picks, not search results; browsing and saving them does not initialize MiniLM or Pinecone.

## Live acceptance checklist

1. Run the app twice; the second unchanged run should report zero new/changed movies.
2. Check the Pinecone namespace contains exactly 30 records after the first run.
3. Test all three assignment queries and inspect titles, ranks, and scores.
4. Test unrelated queries and verify the no-match response; record any threshold adjustment and its rationale.
5. Run `--rag` and ensure recommendations only mention retrieved films.
6. Type `exit` and test blank queries and invalid credentials.

