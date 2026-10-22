"""Evaluate real MiniLM retrieval locally without a Pinecone API key.

This diagnostic uses the same metadata and cosine metric as the application.
It does not replace live Pinecone testing or provide a production fallback.
"""
from movie_finder.search import MODEL_NAME, director_filter, load_movies, movie_text
from sentence_transformers import SentenceTransformer


def main():
    movies = load_movies()
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode([movie_text(m) for m in movies], normalize_embeddings=True)
    queries = [
        'something scary to watch tonight',
        'movies by Christopher Nolan',
        'a feel-good movie about friendship',
        'how to replace a bicycle tire',
        'tax filing instructions for a small business',
        'best recipe for chocolate cake',
    ]
    for query in queries:
        vector = model.encode(query, normalize_embeddings=True)
        scores = embeddings @ vector
        constraint = director_filter(query, movies)
        if constraint:
            director = constraint['director']['$eq']
            scores = scores.copy()
            for i, movie in enumerate(movies):
                if movie['director'] != director:
                    scores[i] = -1
        top = scores.argsort()[::-1][:3]
        print('\n' + query)
        for i in top:
            print(f'  {float(scores[i]):.3f} {movies[i]["title"]}')


if __name__ == '__main__':
    main()
