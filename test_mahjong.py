#!/usr/bin/env python3

"""
# test_mahjong.py

Perform unit testing for `mahjong.py`.

Copyright 2023 Conway
Licensed under MIT No Attribution (MIT-0), see LICENSE.
"""

import unittest

from mahjong import get_duplicates, robust_divide, blunt
from mahjong import ScoreMaster, Game


class TestMahjong(unittest.TestCase):
    def test_get_duplicates(self):
        self.assertEqual(get_duplicates([]), [])
        self.assertEqual(get_duplicates([1, 2, 3]), [])
        self.assertEqual(get_duplicates([1, 1, 2, 3, 'x', 'y', 'x']), [1, 'x'])
        self.assertEqual(get_duplicates(['a', 'b', 'c', 'b']), ['b'])

    def test_robust_divide(self):
        self.assertEqual(robust_divide(0, 0), None)
        self.assertEqual(robust_divide(1, 0), None)
        self.assertAlmostEqual(robust_divide(1, 1), 1)
        self.assertAlmostEqual(robust_divide(1, 2), 0.5)
        self.assertAlmostEqual(robust_divide(100, 2), 50)

    def test_blunt(self):
        self.assertEqual(blunt(None, 1), None)

        self.assertEqual(blunt(0, 1), '0')
        self.assertEqual(blunt(0., 1), '0')
        self.assertEqual(blunt(-0., 1), '0')

        self.assertNotEqual(str(0.1 + 0.2), '0.3')
        self.assertEqual(blunt(0.1 + 0.2, 1), '0.3')

        self.assertEqual(blunt(89640, 1), '89640')
        self.assertEqual(blunt(89640, 2), '89640')
        self.assertEqual(blunt(89640, 3), '89640')
        self.assertEqual(blunt(89640, 4), '89640')

        self.assertEqual(blunt(69.42069, 1), '69.4')
        self.assertEqual(blunt(69.42069, 2), '69.42')
        self.assertEqual(blunt(69.42069, 3), '69.421')
        self.assertEqual(blunt(69.42069, 4), '69.4207')
        self.assertEqual(blunt(69.42069, 5), '69.42069')
        self.assertEqual(blunt(69.42069, 6), '69.42069')

        self.assertEqual(blunt(0.00123456789, 1), '0')
        self.assertEqual(blunt(0.00123456789, 2), '0')
        self.assertEqual(blunt(0.00123456789, 3), '0.001')
        self.assertEqual(blunt(0.00123456789, 4), '0.0012')
        self.assertEqual(blunt(0.00123456789, 5), '0.00123')
        self.assertEqual(blunt(0.00123456789, 6), '0.001235')
        self.assertEqual(blunt(0.00123456789, 7), '0.0012346')
        self.assertEqual(blunt(0.00123456789, 8), '0.00123457')
        self.assertEqual(blunt(0.00123456789, 9), '0.001234568')
        self.assertEqual(blunt(0.00123456789, 10), '0.0012345679')
        self.assertEqual(blunt(0.00123456789, 11), '0.00123456789')
        self.assertEqual(blunt(0.00123456789, 12), '0.00123456789')

    def test_score_master_bad_float(self):
        self.assertRaises(
            ScoreMaster.BadFloatException,
            lambda scores_text: ScoreMaster.parse(scores_text),
            'B=0..1',
        )

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

    def test_score_master_extract_faan(self):
        self.assertEqual(
            ScoreMaster.extract_faan((None, None, None, None), line_number=None),
            (None, None),
        )
        self.assertEqual(
            ScoreMaster.extract_faan((None, None, 13, None), line_number=None),
            (2, 13),
        )
        self.assertEqual(
            ScoreMaster.extract_faan((None, None, 13, None), line_number=None),
            (2, 13),
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

    def test_score_master_extract_blame(self):
        self.assertEqual(
            ScoreMaster.extract_blame((None, None, None, None), line_number=None),
            (None, None),
        )
        self.assertEqual(
            ScoreMaster.extract_blame((None, 'd', None, None), line_number=None),
            (1, 'd'),
        )
        self.assertEqual(
            ScoreMaster.extract_blame((None, None, 'g', None), line_number=None),
            (2, 'g'),
        )
        self.assertEqual(
            ScoreMaster.extract_blame((None, None, None, 'f'), line_number=None),
            (3, 'f'),
        )

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

    def test_game_compute_score_portion(self):
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='half', faan=0), 1)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='half', faan=1), 2)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='half', faan=2), 4)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='half', faan=3), 8)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='half', faan=4), 16)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='half', faan=5), 24)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='half', faan=6), 32)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='half', faan=7), 48)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='half', faan=8), 64)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='half', faan=9), 96)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='half', faan=10), 128)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='half', faan=11), 192)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='half', faan=12), 256)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='half', faan=13), 384)

        self.assertEqual(Game.compute_score_portion(base=1, spiciness='spicy', faan=0), 1)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='spicy', faan=1), 2)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='spicy', faan=2), 4)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='spicy', faan=3), 8)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='spicy', faan=4), 16)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='spicy', faan=5), 32)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='spicy', faan=6), 64)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='spicy', faan=7), 128)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='spicy', faan=8), 256)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='spicy', faan=9), 512)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='spicy', faan=10), 1024)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='spicy', faan=11), 2048)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='spicy', faan=12), 4096)
        self.assertEqual(Game.compute_score_portion(base=1, spiciness='spicy', faan=13), 8192)

        self.assertEqual(Game.compute_score_portion(base=10, spiciness='half', faan=5), 240)
        self.assertEqual(Game.compute_score_portion(base=3, spiciness='spicy', faan=10), 3072)

    def test_game_compute_net_scores(self):
        # Draw (摸和)
        self.assertEqual(
            Game.compute_net_scores(
                base=1, maximum_faan=8, responsibility='full', spiciness='half',
                winner_index=None, winner_faan=None, blame_index=None, blame_type=None,
            ),
            (0, 0, 0, 0),
        )

        # False-win (詐糊)
        self.assertEqual(
            Game.compute_net_scores(
                base=1, maximum_faan=8, responsibility='full', spiciness='half',
                winner_index=None, winner_faan=None, blame_index=1, blame_type='f',
            ),
            (+192, -576, +192, +192),
        )
        self.assertEqual(
            Game.compute_net_scores(
                base=1, maximum_faan=13, responsibility='full', spiciness='half',
                winner_index=None, winner_faan=None, blame_index=1, blame_type='f',
            ),
            (+1152, -3456, +1152, +1152),
        )

        # Self-drawn win (自摸)
        self.assertEqual(
            Game.compute_net_scores(
                base=1, maximum_faan=13, responsibility='full', spiciness='half',
                winner_index=0, winner_faan=0, blame_index=None, blame_type=None,
            ),
            (+3, -1, -1, -1),
        )
        self.assertEqual(
            Game.compute_net_scores(
                base=1, maximum_faan=13, responsibility='full', spiciness='half',
                winner_index=2, winner_faan=4, blame_index=None, blame_type=None,
            ),
            (-16, -16, +48, -16),
        )
        self.assertEqual(
            Game.compute_net_scores(
                base=1, maximum_faan=13, responsibility='full', spiciness='half',
                winner_index=3, winner_faan=8, blame_index=None, blame_type=None,
            ),
            (-64, -64, -64, +192),
        )

        # Discarding at half responsibility (打出半銃)
        self.assertEqual(
            Game.compute_net_scores(
                base=1, maximum_faan=13, responsibility='half', spiciness='half',
                winner_index=1, winner_faan=8, blame_index=2, blame_type='d',
            ),
            (-32, +128, -64, -32),
        )
        self.assertEqual(
            Game.compute_net_scores(
                base=1, maximum_faan=13, responsibility='half', spiciness='spicy',
                winner_index=1, winner_faan=8, blame_index=2, blame_type='d',
            ),
            (-128, +512, -256, -128),
        )

        # Discarding at full responsibility (打出全銃)
        self.assertEqual(
            Game.compute_net_scores(
                base=1, maximum_faan=13, responsibility='full', spiciness='half',
                winner_index=0, winner_faan=8, blame_index=3, blame_type='d',
            ),
            (+128, 0, 0, -128),
        )
        self.assertEqual(
            Game.compute_net_scores(
                base=1, maximum_faan=13, responsibility='full', spiciness='spicy',
                winner_index=0, winner_faan=8, blame_index=3, blame_type='d',
            ),
            (+512, 0, 0, -512),
        )

        # Guaranteeing (包自摸)
        self.assertEqual(
            Game.compute_net_scores(
                base=1, maximum_faan=13, responsibility='full', spiciness='half',
                winner_index=0, winner_faan=0, blame_index=1, blame_type='g',
            ),
            (+3, -3, 0, 0),
        )
        self.assertEqual(
            Game.compute_net_scores(
                base=1, maximum_faan=13, responsibility='full', spiciness='half',
                winner_index=2, winner_faan=4, blame_index=0, blame_type='g',
            ),
            (-48, 0, +48, 0),
        )
        self.assertEqual(
            Game.compute_net_scores(
                base=1, maximum_faan=13, responsibility='full', spiciness='half',
                winner_index=3, winner_faan=8, blame_index=2, blame_type='g',
            ),
            (0, 0, -192, +192),
        )


if __name__ == '__main__':
    unittest.main()
