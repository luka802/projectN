import argparse

from common.llm import ServiceError
from movie_finder.search import MovieFinder, format_results


def main():
    parser = argparse.ArgumentParser(description='Find your next movie with semantic search.')
    parser.add_argument('--rag', action='store_true', help='Add OpenRouter recommendations to retrieved results.')
    args = parser.parse_args()
    print('Welcome to Movie Finder! Loading MiniLM and connecting to Pinecone...')
    try:
        finder = MovieFinder()
        updated = finder.sync()
        print(f'Ready! {updated} new or changed movies indexed. Type exit to quit.')
    except Exception as exc:
        print(f'Could not initialize Movie Finder: {exc}')
        return 1
    while True:
        try:
            query = input('\nWhat would you like to watch? ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nGoodbye! Enjoy your next movie.')
            return 0
        if query.casefold() == 'exit':
            print('Goodbye! Enjoy your next movie.')
            return 0
        if not query:
            print('Describe a movie, genre, mood, or director first.')
            continue
        try:
            movies = finder.search(query)
            print('\n' + format_results(movies))
            if args.rag and movies:
                try:
                    print('\nRecommendation:\n' + finder.recommend(query, movies))
                except ServiceError as exc:
                    print(f'Recommendation unavailable: {exc}. Your search results are shown above.')
        except Exception as exc:
            print(f'Search could not finish: {exc}. Please try again.')


if __name__ == '__main__':
    raise SystemExit(main())
