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
