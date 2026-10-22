"""Small, provider-independent helpers for saved films and readable exports."""
from copy import deepcopy
from movie_finder.search import movie_id


def toggle_saved(saved, movie):
    identifier = movie_id(movie)
    if identifier in saved:
        del saved[identifier]
    else:
        saved[identifier] = deepcopy(movie)


def watchlist_text(movies):
    return '\n\n'.join(
        f'{movie["title"]} ({int(movie["year"])}) — {movie["director"]}\n{movie["description"]}'
        for movie in movies
    )


def poster_style(movie):
    """Choose original artwork without requiring remote poster APIs."""
    specific = {'Interstellar': 'interstellar', 'Inception': 'inception', 'Memento': 'memento'}
    if movie['title'] in specific:
        return f"background-image:url('app/static/art/{specific[movie['title']]}.png');background-size:cover;background-position:center"
    genre = movie.get('genre', '').casefold()
    if 'horror' in genre:
        position = '0% 14.5%'
    elif 'animation' in genre or 'fantasy' in genre or 'family' in genre:
        position = '100% 14.5%'
    elif 'romance' in genre or 'musical' in genre:
        position = '0% 85.5%'
    elif 'science fiction' in genre:
        position = '100% 85.5%'
    elif any(value in genre for value in ('action', 'thriller', 'crime', 'war')):
        position = '50% 85.5%'
    else:
        position = '50% 14.5%'
    return f"background-image:url('app/static/art/genres.png');background-size:300% auto;background-position:{position}"
