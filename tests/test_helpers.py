import unittest
from ui_helpers import toggle_saved, watchlist_text


class SavedFilmTests(unittest.TestCase):
    def test_save_remove_and_export_without_duplicates(self):
        saved = {}
        movie = {'title': 'Example', 'year': 2000, 'director': 'Director', 'description': 'A story.'}
        toggle_saved(saved, movie)
        self.assertEqual(len(saved), 1)
        movie['description'] = 'A change outside the watchlist.'
        self.assertIn('A story.', watchlist_text(saved.values()))
        self.assertIn('Example (2000)', watchlist_text(saved.values()))
        toggle_saved(saved, movie)
        self.assertEqual(saved, {})
