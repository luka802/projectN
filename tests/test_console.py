import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

from movie_finder.__main__ import main as movie_main
from travel_buddy.__main__ import main as travel_main


class ConsoleTests(unittest.TestCase):
    @patch('travel_buddy.bot.chat', side_effect=KeyboardInterrupt)
    @patch('builtins.input', return_value='somewhere outdoors and peaceful')
    def test_travel_interrupt_during_model_call_says_goodbye(self, user_input, llm):
        output = io.StringIO()
        with redirect_stdout(output):
            travel_main()
        self.assertIn('Goodbye', output.getvalue())

    @patch('sys.argv', ['movie_finder'])
    @patch('movie_finder.__main__.MovieFinder')
    @patch('builtins.input', return_value='friendship')
    def test_movie_interrupt_during_search_says_goodbye(self, user_input, factory):
        finder = Mock()
        finder.sync.return_value = 0
        finder.search.side_effect = KeyboardInterrupt
        factory.return_value = finder
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(movie_main(), 0)
        self.assertIn('Goodbye', output.getvalue())
