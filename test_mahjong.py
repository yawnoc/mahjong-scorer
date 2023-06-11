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

    def test_score_master_multiple_winners(self):
        self.assertRaises(
            ScoreMaster.MultipleWinnersException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A B C D \n 0 0 - -',
        )
        self.assertRaises(
            ScoreMaster.MultipleWinnersException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A B C D \n 0 - 8 -',
        )
        self.assertRaises(
            ScoreMaster.MultipleWinnersException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A B C D \n d 4 - 6',
        )
        try:
            ScoreMaster.parse('A B C D \n d - 7 -')
        except ScoreMaster.MultipleWinnersException:
            self.fail('ScoreMaster.MultipleWinnersException raised erroneously')

    def test_score_master_multiple_blame(self):
        self.assertRaises(
            ScoreMaster.MultipleBlameException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A B C D \n 3 d d -',
        )
        self.assertRaises(
            ScoreMaster.MultipleBlameException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A B C D \n 4 - d g',
        )
        self.assertRaises(
            ScoreMaster.MultipleBlameException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A B C D \n 5 f d g',
        )
        try:
            ScoreMaster.parse('A B C D \n 6 - d -')
        except ScoreMaster.MultipleBlameException:
            self.fail('ScoreMaster.MultipleBlameException raised erroneously')
        try:
            ScoreMaster.parse('A B C D \n - 7 - -')
        except ScoreMaster.MultipleBlameException:
            self.fail('ScoreMaster.MultipleBlameException raised erroneously')

    def test_score_master_no_win_yet_non_false_blame(self):
        self.assertRaises(
            ScoreMaster.NoWinYetNonFalseBlameException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A B C D \n d - - -',
        )
        self.assertRaises(
            ScoreMaster.NoWinYetNonFalseBlameException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A B C D \n - - g -',
        )
        try:
            ScoreMaster.parse('A B C D \n - - 3 -')
        except ScoreMaster.NoWinYetNonFalseBlameException:
            self.fail('ScoreMaster.NoWinYetNonFalseBlameException raised erroneously')
        try:
            ScoreMaster.parse('A B C D \n - - f -')
        except ScoreMaster.NoWinYetNonFalseBlameException:
            self.fail('ScoreMaster.NoWinYetNonFalseBlameException raised erroneously')
        try:
            ScoreMaster.parse('A B C D \n - - - -')
        except ScoreMaster.NoWinYetNonFalseBlameException:
            self.fail('ScoreMaster.NoWinYetNonFalseBlameException raised erroneously')

    def test_score_master_win_yet_false_blame(self):
        self.assertRaises(
            ScoreMaster.WinYetFalseBlameException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A B C D \n 1 f - -',
        )
        self.assertRaises(
            ScoreMaster.WinYetFalseBlameException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'A B C D \n - - f 13',
        )
        try:
            ScoreMaster.parse('A B C D \n - f - -')
        except ScoreMaster.WinYetFalseBlameException:
            self.fail('ScoreMaster.WinYetFalseBlameException raised erroneously')
        try:
            ScoreMaster.parse('A B C D \n - - - -')
        except ScoreMaster.WinYetFalseBlameException:
            self.fail('ScoreMaster.WinYetFalseBlameException raised erroneously')


if __name__ == '__main__':
    unittest.main()
