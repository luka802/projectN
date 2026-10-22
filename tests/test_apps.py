import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import numpy as np

from common.llm import ServiceError, chat
from movie_finder.search import MovieFinder, content_hash, load_movies, movie_id
from travel_buddy.bot import ACTIVITIES, TravelBuddy


class TravelTests(unittest.TestCase):
    @patch('travel_buddy.bot.chat')
    def test_trip_history_context_and_activity_constraints(self, llm):
        bot = TravelBuddy()
        bot.start()
        llm.side_effect = [json.dumps({'choice': x}) for x in ['Mountains', 'Camping', 'Stargazing']]
        bot.reply('2')
        bot.reply('camp outdoors')
        self.assertEqual(bot.options, ACTIVITIES['Mountains'])
        result = bot.reply('look at stars')
        self.assertIn('Mountains', result)
        self.assertIn('Camping', result)
        self.assertIn('Stargazing', result)
        self.assertTrue(bot.complete)
        self.assertIn('camp outdoors', str(llm.call_args.args[0]))
        self.assertEqual(len(bot.history), 7)

    @patch('travel_buddy.bot.chat')
    def test_invalid_and_malformed_answers_do_not_advance(self, llm):
        bot = TravelBuddy()
        llm.side_effect = ['{"choice": null}', '{"choice":"Scuba diving"}', 'not json', '[]']
        for text in ['Moon', 'scuba', 'nonsense', 'nothing']:
            bot.reply(text)
            self.assertEqual(bot.choices, [])

    @patch('travel_buddy.bot.chat', side_effect=ServiceError('Unavailable'))
    def test_api_failure_preserves_choices(self, llm):
        bot = TravelBuddy(choices=['Beach'])
        self.assertIn('saved', bot.reply('1'))
        self.assertEqual(bot.choices, ['Beach'])

    @patch('travel_buddy.bot.chat')
    def test_exit_does_not_call_service(self, llm):
        for choices in ([], ['Mountains'], ['Beach', 'Camping', 'Snorkeling']):
            bot = TravelBuddy(choices=choices)
            self.assertIn('Goodbye', bot.reply(' EXIT '))
            self.assertTrue(bot.closed)
        llm.assert_not_called()

    def test_restart_and_empty_input(self):
        bot = TravelBuddy(choices=['Mountains'])
        bot.reply('restart')
        self.assertEqual(bot.choices, [])
        self.assertIn('trip type', bot.reply(''))


class MemoryIndex:
    def __init__(self):
        self.records = {}
        self.upsert_count = 0
        self.matches = []

    def fetch(self, ids, namespace):
        return SimpleNamespace(vectors={key: self.records[key] for key in ids if key in self.records})

    def upsert(self, vectors, namespace):
        self.upsert_count += 1
        for vector in vectors:
            self.records[vector['id']] = SimpleNamespace(metadata=vector['metadata'])

    def query(self, **kwargs):
        self.last_query = kwargs
        return SimpleNamespace(matches=self.matches)


class MovieTests(unittest.TestCase):
    def setUp(self):
        self.index = MemoryIndex()
        self.encoder = Mock()
        self.encoder.encode.side_effect = lambda texts, **kw: np.ones((len(texts), 384)) if isinstance(texts, list) else np.ones(384)
        self.finder = MovieFinder(encoder=self.encoder, index=self.index)

    def test_dataset_and_repeated_ingestion(self):
        movies = load_movies()
        self.assertEqual(len(movies), 30)
        self.assertEqual(self.finder.sync(), 30)
        self.assertEqual(self.finder.sync(), 0)
        self.assertEqual(len(self.index.records), 30)
        self.assertEqual(self.index.upsert_count, 1)
        self.encoder.encode.assert_called_once()

    def test_edited_metadata_updates_same_id(self):
        self.finder.sync()
        movies = load_movies()
        identifier = movie_id(movies[0])
        movies[0]['description'] += ' Additional context.'
        self.assertEqual(movie_id(movies[0]), identifier)
        with patch('movie_finder.search.load_movies', return_value=movies):
            self.assertEqual(self.finder.sync(), 1)
        self.assertEqual(len(self.index.records), 30)
        self.assertEqual(self.index.records[identifier].metadata['content_hash'], content_hash(movies[0]))

    def test_threshold_filters_each_result_and_asks_for_top_three(self):
        self.finder.threshold = 0.35
        self.index.matches = [SimpleNamespace(score=score, metadata={'title': str(score)}) for score in [0.8, 0.35, 0.2]]
        result = self.finder.search('friendship')
        self.assertEqual(len(result), 2)
        self.assertEqual(self.index.last_query['top_k'], 3)
        self.assertTrue(self.index.last_query['include_metadata'])
        self.assertEqual(len(self.index.last_query['vector']), 384)

    def test_explicit_director_uses_metadata_filter(self):
        self.finder.search('movies by Christopher Nolan')
        self.assertEqual(self.index.last_query['filter'], {'director': {'$eq': 'Christopher Nolan'}})
        self.finder.search('a movie about friendship')
        self.assertNotIn('filter', self.index.last_query)

    def test_pinecone_numeric_year_is_displayed_as_integer(self):
        self.index.matches = [SimpleNamespace(score=0.8, metadata={'title': 'Example', 'year': 2000.0})]
        self.assertEqual(self.finder.search('example')[0]['year'], 2000)
        self.assertIsInstance(self.finder.search('example')[0]['year'], int)

    @patch('movie_finder.search.chat')
    def test_no_match_skips_llm(self, llm):
        self.assertEqual(self.finder.search(''), [])
        self.assertIn("couldn't find", self.finder.recommend('no match', []))
        llm.assert_not_called()

    @patch('movie_finder.search.chat', return_value='Try this film.')
    def test_rag_receives_retrieved_context(self, llm):
        movies = [{'title': 'Example', 'year': 2000, 'score': 0.5}]
        self.finder.recommend('friendship', movies)
        context = json.loads(llm.call_args.args[0][1]['content'])
        self.assertEqual(context['retrieved_movies'], movies)


class OpenRouterTests(unittest.TestCase):
    @patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test', 'OPENROUTER_MODEL': 'primary', 'OPENROUTER_FALLBACK_MODEL': 'fallback'})
    @patch('common.llm.requests.post')
    def test_model_unavailable_uses_fallback(self, post):
        post.side_effect = [Mock(status_code=404), Mock(status_code=200, ok=True, json=lambda: {'choices': [{'message': {'content': 'Hello'}}]})]
        self.assertEqual(chat([{'role': 'user', 'content': 'Hi'}]), 'Hello')
        self.assertEqual(post.call_args.kwargs['json']['model'], 'fallback')

    @patch.dict(os.environ, {'OPENROUTER_API_KEY': ''})
    def test_missing_key_has_clear_error(self):
        with self.assertRaisesRegex(ServiceError, 'OPENROUTER_API_KEY'):
            chat([])


if __name__ == '__main__':
    unittest.main()
