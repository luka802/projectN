"""UI regressions run with fake providers; no API keys or model download required."""
import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import streamlit as st
from streamlit.testing.v1 import AppTest

from movie_finder.search import load_movies

APP = str(Path(__file__).resolve().parents[1] / 'web_app.py')


def click(app, label):
    next(button for button in app.button if button.label == label).click().run()
    assert not app.exception, app.exception


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        st.cache_resource.clear()

    @patch('movie_finder.search.MovieFinder')
    def test_featured_home_and_saved_navigation_need_no_search(self, factory):
        app = AppTest.from_file(APP).run()
        self.assertEqual(app.radio[0].value, 'Find a film')
        self.assertFalse(app.exception)
        factory.assert_not_called()
        click(app, 'Save Interstellar for later +')
        app.radio[0].set_value('Saved films').run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.session_state.saved_movies), 1)
        click(app, 'Remove Interstellar')
        self.assertEqual(len(app.session_state.saved_movies), 0)
        factory.assert_not_called()

    @patch('travel_buddy.bot.chat')
    def test_guided_travel_back_and_completed_plan(self, llm):
        llm.side_effect = [json.dumps({'choice': x}) for x in ['Mountains', 'Beach', 'Camping', 'Snorkeling']]
        app = AppTest.from_file(APP).run()
        app.radio[0].set_value('Plan a getaway').run()
        self.assertFalse(app.exception)
        click(app, 'Choose Mountains')
        self.assertEqual(app.session_state.travel.choices, ['Mountains'])
        click(app, '← Back a step')
        self.assertEqual(app.session_state.travel.choices, [])
        click(app, 'Choose Beach')
        click(app, 'Choose Camping')
        click(app, 'Choose Snorkeling')
        self.assertTrue(app.session_state.travel.complete)
        self.assertEqual(len(app.get('download_button')), 1)
        click(app, 'Change stay')
        self.assertEqual(app.session_state.travel.choices, ['Beach'])
        click(app, 'Start a new trip ↗')
        self.assertEqual(app.session_state.travel.choices, [])
        llm.assert_not_called()

    @patch('movie_finder.search.MovieFinder')
    def test_search_suggestions_persistence_recommendation_and_recovery(self, factory):
        finder = Mock()
        movies = [{**m, 'score': 0.5} for m in load_movies()[:3]]
        finder.search.return_value = movies
        finder.recommend.return_value = 'A recommendation using your retrieved films.'
        factory.return_value = finder
        app = AppTest.from_file(APP).run()
        app.radio[0].set_value('Find a film').run()
        self.assertFalse(app.exception)
        click(app, 'A Nolan night')
        finder.search.assert_called_once_with('movies by Christopher Nolan')
        self.assertEqual(app.text_input[0].value, 'movies by Christopher Nolan')
        self.assertEqual(len(app.session_state.movie_results), 3)
        click(app, f'Save {movies[0]["title"]} for later +')
        self.assertEqual(len(app.session_state.saved_movies), 1)
        self.assertEqual(finder.search.call_count, 1)
        click(app, 'Help me choose ✦')
        self.assertIn('recommendation', app.session_state.movie_recommendation)
        self.assertEqual(len(app.session_state.saved_movies), 1)
        self.assertEqual(finder.search.call_count, 1)
        app.radio[0].set_value('Plan a getaway').run()
        app.radio[0].set_value('Find a film').run()
        self.assertEqual(len(app.session_state.movie_results), 3)
        self.assertEqual(app.text_input[0].value, 'movies by Christopher Nolan')
        self.assertIn('recommendation', app.session_state.movie_recommendation)
        finder.search.side_effect = RuntimeError('Unavailable')
        click(app, 'A little suspense')
        self.assertTrue(app.error)
        self.assertEqual(len(app.session_state.movie_results), 3)
        finder.search.side_effect = None
        finder.search.return_value = []
        click(app, 'Something feel-good')
        self.assertEqual(app.session_state.movie_results, [])
        self.assertNotIn('movie_recommendation', app.session_state)


if __name__ == '__main__':
    unittest.main()
