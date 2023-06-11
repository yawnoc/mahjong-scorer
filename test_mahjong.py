#!/usr/bin/env python3

"""
# test_mahjong.py

Perform unit testing for `mahjong.py`.

Copyright 2023 Conway
Licensed under MIT No Attribution (MIT-0), see LICENSE.
"""

import unittest

from mahjong import get_duplicates
from mahjong import ScoreMaster


class TestMahjong(unittest.TestCase):
    def test_get_duplicates(self):
        self.assertEqual(get_duplicates([]), [])
        self.assertEqual(get_duplicates([1, 2, 3]), [])
        self.assertEqual(get_duplicates([1, 1, 2, 3, 'x', 'y', 'x']), [1, 'x'])
        self.assertEqual(get_duplicates(['a', 'b', 'c', 'b']), ['b'])

    def test_score_master_parse_duplicate_names(self):
        self.assertRaises(
            ScoreMaster.DuplicatePlayerNamesException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A A B C',
        )
        self.assertRaises(
            ScoreMaster.DuplicatePlayerNamesException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A A A A',
        )
        try:
            ScoreMaster.parse('A B C D')
        except ScoreMaster.DuplicatePlayerNamesException:
            self.fail('ScoreMaster.DuplicatePlayerNamesException raised erroneously')

    def test_score_master_no_players(self):
        self.assertRaises(
            ScoreMaster.NoPlayersException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            '0 1 2 3',
        )


if __name__ == '__main__':
    unittest.main()
