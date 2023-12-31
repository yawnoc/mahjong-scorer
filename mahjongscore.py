#!/usr/bin/env python3

"""
# mahjongscore.py

A Python scorer for Mahjong (HK rules).

Copyright 2023 Conway
Licensed under MIT No Attribution (MIT-0), see LICENSE.
"""

import argparse
import csv
import math
import os
import re
import sys

__version__ = '0.3.0'
DEFAULT_BASE = 1
DEFAULT_MAXIMUM_FAAN = 13
DEFAULT_RESPONSIBILITY = 'full'
DEFAULT_SPICINESS = 'half'


def get_duplicates(iterable):
    seen_items = set()
    duplicate_items = []
    for item in iterable:
        if item in seen_items:
            duplicate_items.append(item)
        else:
            seen_items.add(item)

    return duplicate_items


def robust_divide(dividend, divisor):
    try:
        return dividend / divisor
    except ZeroDivisionError:
        return None


def blunt(number, max_decimal_places=4, none_to_nan=False):
    """
    Round a number to at most certain decimal places, as a string.
    """
    if number is None:
        if none_to_nan:
            return 'nan'
        else:
            return None

    if number == 0:
        return '0'

    nice_string = f'{number :.{max_decimal_places}F}'
    nice_string = re.sub(r'[.]?0*$', '', nice_string)

    return nice_string


class ScoreMaster:
    def __init__(self, scores_text, start_date, end_date):
        self.players_including_everyone, self.games = ScoreMaster.parse(scores_text, start_date, end_date)

    LINE_EXPLAINER = (
        f'A line must have one of the following forms:\n'
        f'    <yyyy>-<mm>-<dd>     # a date\n'
        f'    B=<base>             # a declaration of base points (default {DEFAULT_BASE}),\n'
        f'                         #   0.5 = two & five chicken (二五雞)\n'
        f'                         #   1   = five & one (五一)\n'
        f'                         #   2   = one & two bucks (一二蚊)\n'
        f'    M=<faan>             # a declaration of maximum faan (default {DEFAULT_MAXIMUM_FAAN})\n'
        f'    R=half | full        # a declaration of responsibility (default {DEFAULT_RESPONSIBILITY})\n'
        f'                         #   half  = half responsibility (半銃)\n'
        f'                         #   full  = full responsibility (全銃)\n'
        f'    S=half | spicy       # a declaration of spiciness (default {DEFAULT_SPICINESS})\n'
        f'                         #   half  = half-spicy rise (半辣上)\n'
        f'                         #   spicy = spicy-spicy rise (辣辣上)\n'
        f'    <P1> <P2> <P3> <P4>  # a declaration of player names (no hashes,\n'
        f'                         # asterisks, leading hyphens, or leading digits)\n'
        f'    <R1> <R2> <R3> <R4>  # a declaration of game results\n'
        f"                         #   <digits> = winner's faan\n"
        f'                         #   -        = blameless player\n'
        f'                         #   d        = discarding (打出) player\n'
        f'                         #   D        = discard-guaranteeing (包打出) player\n'
        f'                         #   S        = self-draw-guaranteeing (包自摸) player\n'
        f'                         #   f        = false-winning (詐糊) player\n'
        f'    # <comment>          # a comment, also allowed at the end of the forms\n'
        f'                         # above\n'
        f'All other lines are invalid.\n'
    )

    @staticmethod
    def parse(scores_text, start_date=None, end_date=None):
        player_from_name = {}
        games = []

        date = None
        base = DEFAULT_BASE
        maximum_faan = DEFAULT_MAXIMUM_FAAN
        responsibility = DEFAULT_RESPONSIBILITY
        spiciness = DEFAULT_SPICINESS
        names = None

        lines = scores_text.splitlines()
        for line_number, line in enumerate(lines, start=1):

            date_line_match = ScoreMaster.match_date_line(line)
            if date_line_match:
                new_date = date_line_match.group('date')
                if date is not None and new_date < date:
                    raise ScoreMaster.BadChronologyException(
                        line_number,
                        f'bad chronological order {new_date} < {date}',
                    )
                date = new_date
                continue

            if start_date is not None:
                if date is None or date < start_date:
                    continue

            if end_date is not None:
                if date is None or date >= end_date:
                    continue

            base_line_match = ScoreMaster.match_base_line(line)
            if base_line_match:
                base_str = base_line_match.group('base')
                try:
                    base = float(base_str)
                except ValueError:
                    raise ScoreMaster.BadFloatException(
                        line_number,
                        f'unable to convert {base_str} to float',
                    )
                continue

            maximum_line_match = ScoreMaster.match_maximum_line(line)
            if maximum_line_match:
                maximum_faan = int(maximum_line_match.group('maximum_faan'))
                continue

            responsibility_line_match = ScoreMaster.match_responsibility_line(line)
            if responsibility_line_match:
                responsibility = responsibility_line_match.group('responsibility')
                continue

            spiciness_line_match = ScoreMaster.match_spiciness_line(line)
            if spiciness_line_match:
                spiciness = spiciness_line_match.group('spiciness')
                continue

            players_line_match = ScoreMaster.match_players_line(line)
            if players_line_match:
                names = tuple(
                    players_line_match.group(f'name_{i}')
                    for i in range(0, 4)
                )

                duplicate_names = get_duplicates(names)
                if duplicate_names:
                    raise ScoreMaster.DuplicatePlayerNamesException(
                        line_number,
                        f'duplicate player names {duplicate_names}',
                    )

                for name in names:
                    if name not in player_from_name:
                        player_from_name[name] = Player(name)
                continue

            game_line_match = ScoreMaster.match_game_line(line)
            if game_line_match:
                if names is None:
                    raise ScoreMaster.NoPlayersException(
                        line_number,
                        f'game declared without first declaring player names',
                    )

                faans = tuple(
                    ScoreMaster.normalise_faan(game_line_match.group(f'faan_{i}'))
                    for i in range(0, 4)
                )
                winner_index, winner_faan = ScoreMaster.extract_faan(faans, maximum_faan, line_number)

                blames = tuple(
                    ScoreMaster.normalise_blame(game_line_match.group(f'blame_{i}'))
                    for i in range(0, 4)
                )
                blame_index, blame_type = ScoreMaster.extract_blame(blames, line_number)

                if winner_index is None:
                    if blame_type is not None and blame_type != 'f':
                        raise ScoreMaster.NoWinYetNonFalseBlameException(
                            line_number,
                            f'game declared with no winner yet non-false-win blame (suffix `d`, `D`, or `S`)',
                        )
                else:
                    if blame_type == 'f':
                        raise ScoreMaster.WinYetFalseBlameException(
                            line_number,
                            f'game declared with winner yet false-win blame (suffix `f`)',
                        )

                if responsibility == 'full' and blame_type == 'D':
                    raise ScoreMaster.RedundantDiscardGuaranteeException(
                        line_number,
                        f'discard-guarantee `D` is redundant under full responsibility (全銃)',
                    )

                games.append(
                    Game(
                        date, base, maximum_faan, responsibility, spiciness,
                        names, winner_index, winner_faan, blame_index, blame_type,
                    )
                )
                continue

            if ScoreMaster.match_comment_line(line):
                continue

            raise ScoreMaster.InvalidLineException(
                line_number,
                f'invalid line\n\n{ScoreMaster.LINE_EXPLAINER}',
            )

        for game in games:
            game.update(player_from_name)

        players = list(player_from_name.values())
        everyone = Player('*')
        everyone.game_count = sum(p.game_count for p in players)
        everyone.win_count = sum(p.win_count for p in players)
        everyone.blame_count = sum(p.blame_count for p in players)
        everyone.net_score = sum(p.net_score for p in players)

        players_including_everyone = players + [everyone]

        for player in players_including_everyone:
            player.update_averages()

        return players_including_everyone, games

    @staticmethod
    def match_date_line(line):
        return re.fullmatch(
            pattern=r'''
                ^ [\s]*
                (?P<date> [0-9]{4} - [0-9]{2} - [0-9]{2} )
                [\s]* (?: [#] .* )? $
            ''',
            string=line,
            flags=re.VERBOSE,
        )

    @staticmethod
    def match_base_line(line):
        return re.fullmatch(
            pattern=fr'''
                ^ [\s]*
                B=(?P<base> [.0-9]+ )
                [\s]* (?: [#] .* )? $
            ''',
            string=line,
            flags=re.VERBOSE,
        )

    @staticmethod
    def match_maximum_line(line):
        return re.fullmatch(
            pattern=fr'''
                ^ [\s]*
                M=(?P<maximum_faan> [0-9]+ )
                [\s]* (?: [#] .* )? $
            ''',
            string=line,
            flags=re.VERBOSE,
        )

    @staticmethod
    def match_responsibility_line(line):
        return re.fullmatch(
            pattern=fr'''
                ^ [\s]*
                R=(?P<responsibility> half | full )
                [\s]* (?: [#] .* )? $
            ''',
            string=line,
            flags=re.VERBOSE,
        )

    @staticmethod
    def match_spiciness_line(line):
        return re.fullmatch(
            pattern=fr'''
                ^ [\s]*
                S=(?P<spiciness> half | spicy )
                [\s]* (?: [#] .* )? $
            ''',
            string=line,
            flags=re.VERBOSE,
        )

    @staticmethod
    def match_players_line(line):
        player_name_regex = r'[^\s#*0-9-][^\s#*]*'
        return re.fullmatch(
            pattern=fr'''
                ^ [\s]*
                (?P<name_0> {player_name_regex} )
                    [\s]+
                (?P<name_1> {player_name_regex} )
                    [\s]+
                (?P<name_2> {player_name_regex} )
                    [\s]+
                (?P<name_3> {player_name_regex} )
                [\s]* (?: [#] .* )? $
            ''',
            string=line,
            flags=re.VERBOSE,
        )

    @staticmethod
    def match_game_line(line):
        faan_regex = '[0-9]+'
        blame_regex = '[-dDSf]'  # null, discard, discard-guarantee, self-draw-guarantee, or false-win
        return re.fullmatch(
            pattern=fr'''
                ^ [\s]*
                (?: (?P<faan_0> {faan_regex} ) | (?P<blame_0> {blame_regex} )  )
                    [\s]+
                (?: (?P<faan_1> {faan_regex} ) | (?P<blame_1> {blame_regex} )  )
                    [\s]+
                (?: (?P<faan_2> {faan_regex} ) | (?P<blame_2> {blame_regex} )  )
                    [\s]+
                (?: (?P<faan_3> {faan_regex} ) | (?P<blame_3> {blame_regex} )  )
                [\s]* (?: [#] .* )? $
            ''',
            string=line,
            flags=re.VERBOSE,
        )

    @staticmethod
    def match_comment_line(line):
        return re.fullmatch(
            pattern=r'^ [\s]* (?: [#] .* )? $',
            string=line,
            flags=re.VERBOSE,
        )

    @staticmethod
    def normalise_faan(faan_string):
        try:
            return int(faan_string)
        except TypeError:
            return None

    @staticmethod
    def normalise_blame(blame_string):
        if blame_string is None:
            return None

        if blame_string == '-':
            return None

        return blame_string

    @staticmethod
    def extract_faan(faans, maximum_faan, line_number):
        faan_indices = set(i for i in range(0, 4) if faans[i] is not None)

        if len(faan_indices) > 1:
            raise ScoreMaster.MultipleWinnersException(
                line_number,
                f'game declared with multiple winners (digits entries)',
            )

        try:
            winner_index = faan_indices.pop()
            winner_faan = faans[winner_index]
        except KeyError:
            winner_index = None
            winner_faan = None

        if winner_faan is not None and winner_faan > maximum_faan:
            raise ScoreMaster.MaximumFaanExceededException(
                line_number,
                f"game declared with winner's faan exceeding maximum faan ({maximum_faan})",
            )

        return winner_index, winner_faan

    @staticmethod
    def extract_blame(blames, line_number):
        blame_indices = set(i for i in range(0, 4) if blames[i] is not None)

        if len(blame_indices) > 1:
            raise ScoreMaster.MultipleBlameException(
                line_number,
                f'game declared with multiple players blamed (suffix `d`, `S`, or `f`)',
            )

        try:
            blame_index = blame_indices.pop()
            blame_type = blames[blame_index]
        except KeyError:
            blame_index = None
            blame_type = None

        return blame_index, blame_type

    def write_tsv(self, file_name):
        with open(file_name, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file, delimiter='\t', lineterminator=os.linesep)
            writer.writerow([
                'name',
                'game_count',
                'win_count',
                'win_fraction',
                'blame_count',
                'blame_fraction',
                'net_score',
                'net_score_per_game',
            ])
            for player in sorted(self.players_including_everyone):
                writer.writerow([
                    player.name,
                    player.game_count,
                    player.win_count,
                    blunt(player.win_fraction, none_to_nan=True),
                    player.blame_count,
                    blunt(player.blame_fraction, none_to_nan=True),
                    blunt(player.net_score, none_to_nan=True),
                    blunt(player.net_score_per_game, none_to_nan=True),
                ])

    class BadLineException(Exception):
        def __init__(self, line_number, message):
            self.line_number = line_number
            self.message = message

    class BadChronologyException(BadLineException):
        pass

    class BadFloatException(BadLineException):
        pass

    class DuplicatePlayerNamesException(BadLineException):
        pass

    class NoPlayersException(BadLineException):
        pass

    class InvalidLineException(BadLineException):
        pass

    class MultipleWinnersException(BadLineException):
        pass

    class MaximumFaanExceededException(BadLineException):
        pass

    class MultipleBlameException(BadLineException):
        pass

    class NoWinYetNonFalseBlameException(BadLineException):
        pass

    class WinYetFalseBlameException(BadLineException):
        pass

    class RedundantDiscardGuaranteeException(BadLineException):
        pass


class Player:
    def __init__(self, name):
        self.name = name

        self.game_count = 0
        self.win_count = 0
        self.blame_count = 0
        self.net_score = 0

        self.win_fraction = 0
        self.blame_fraction = 0
        self.net_score_per_game = 0

    def __lt__(self, other):
        return self.rank() < other.rank()

    def rank(self):
        is_everyone = self.name == '*'
        net_score_per_game = (
            -math.inf if self.net_score_per_game is None
            else self.net_score_per_game
        )
        name = self.name

        return is_everyone, -net_score_per_game, name

    def update_averages(self):
        self.win_fraction = robust_divide(self.win_count, self.game_count)
        self.blame_fraction = robust_divide(self.blame_count, self.game_count)
        self.net_score_per_game = robust_divide(self.net_score, self.game_count)


class Game:
    def __init__(self, date, base, maximum_faan, responsibility, spiciness,
                 names, winner_index, winner_faan, blame_index, blame_type):
        self.date = date

        self.base = base
        self.maximum_faan = maximum_faan
        self.responsibility = responsibility
        self.spiciness = spiciness

        self.names = names
        self.winner_index = winner_index
        self.winner_faan = winner_faan
        self.blame_index = blame_index
        self.blame_type = blame_type

    def update(self, player_from_name):
        net_scores = Game.compute_net_scores(
            self.base, self.maximum_faan, self.responsibility, self.spiciness,
            self.winner_index, self.winner_faan, self.blame_index, self.blame_type,
        )

        for index, name in enumerate(self.names):
            player = player_from_name[name]
            player.game_count += 1
            player.win_count += 1 if index == self.winner_index else 0
            player.blame_count += 1 if index == self.blame_index else 0
            player.net_score += net_scores[index]

    @staticmethod
    def compute_net_scores(
        base, maximum_faan, responsibility, spiciness,
        winner_index, winner_faan, blame_index, blame_type
    ):
        if winner_index is None:  # no win

            if blame_index is None:  # draw (摸和)
                # Scores do not change.
                return (0, 0, 0, 0)

            elif blame_type == 'f':  # false-win (詐糊)
                # Blamed player pays each other player the maximum self-drawn win (i.e. three portions).
                portion = Game.compute_score_portion(base, spiciness, faan=maximum_faan)
                return tuple(
                    (-9 * portion) if i == blame_index else
                    (+3 * portion)
                    for i in range(0, 4)
                )

            raise RuntimeError(
                'Implementation error: `ScoreMaster.NoWinYetNonFalseBlameException` ought to have been raised'
            )

        else:  # win

            portion = Game.compute_score_portion(base, spiciness, faan=winner_faan)

            if blame_index is None:  # self-drawn win (自摸)
                # Blameless players each pay winner one portion.
                return tuple(
                    (+3 * portion) if i == winner_index else
                    (-portion)
                    for i in range(0, 4)
                )

            elif blame_type == 'd':  # discarding (打出)

                if responsibility == 'half':  # half responsibility (半銃)
                    # Blamed player pays winner one portion; blameless players each pay winner a half portion.
                    return tuple(
                        (+2 * portion) if i == winner_index else
                        (-portion) if i == blame_index else
                        (-portion/2)
                        for i in range(0, 4)
                    )

                elif responsibility == 'full':  # full responsibility (全銃)
                    # Blamed player pays winner a double portion.
                    return tuple(
                        (+2 * portion) if i == winner_index else
                        (-2 * portion) if i == blame_index
                        else 0
                        for i in range(0, 4)
                    )

                raise RuntimeError(
                    'Implementation error: `responsibility` is neither `half` nor `full`'
                )

            elif blame_type == 'D':  # discard-guaranteeing (包打出)
                # Blamed player pays winner a double portion; same as full responsibility (全銃).
                return tuple(
                    (+2 * portion) if i == winner_index else
                    (-2 * portion) if i == blame_index
                    else 0
                    for i in range(0, 4)
                )

            elif blame_type == 'S':  # self-draw-guaranteeing (包自摸)
                # Blamed player pays winner three portions.
                return tuple(
                    (+3 * portion) if i == winner_index else
                    (-3 * portion) if i == blame_index
                    else 0
                    for i in range(0, 4)
                )

            raise RuntimeError(
                'Implementation error: `ScoreMaster.WinYetFalseBlameException` ought to have been raised'
            )

    @staticmethod
    def compute_score_portion(base, spiciness, faan):
        if spiciness == 'half':  # half-spicy rise (半辣上)
            if faan <= 4:
                multiplier = 2 ** faan
            else:
                index = 4 + (faan - 4) // 2
                if faan % 2 == 0:
                    multiplier = 2 ** index
                else:
                    multiplier = 2 ** index * 3 // 2

        elif spiciness == 'spicy':  # spicy-spicy rise (辣辣上)
            multiplier = 2 ** faan

        else:
            raise RuntimeError(
                'Implementation error: `spiciness` is neither `half` nor `spicy`'
            )

        return base * multiplier


def parse_command_line_arguments():
    argument_parser = argparse.ArgumentParser(
        description='Score some games of Mahjong (HK rules).'
    )
    argument_parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'{argument_parser.prog} version {__version__}'
    )
    argument_parser.add_argument(
        'scores_file_name',
        help='name of scores file; output written to `{scores.txt}.tsv`',
        metavar='scores.txt',
    )
    argument_parser.add_argument(
        '--from',
        dest='start_date',
        help='start date for scoring (inclusive)',
        metavar='yyyy-mm-dd',
    )
    argument_parser.add_argument(
        '--to',
        dest='end_date',
        help='end date for scoring (exclusive)',
        metavar='yyyy-mm-dd',
    )

    return argument_parser.parse_args()


def read_scores_text(scores_file_name):
    if os.path.isdir(scores_file_name):
        print(
            f'Error: `{scores_file_name}` is a directory, not a file',
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        with open(scores_file_name, 'r', encoding='utf-8') as scores_file:
            scores_text = scores_file.read()
    except FileNotFoundError:
        print(
            f'Error: file `{scores_file_name}` not found',
            file=sys.stderr,
        )
        sys.exit(1)

    return scores_text


def main():
    parsed_arguments = parse_command_line_arguments()
    scores_file_name = parsed_arguments.scores_file_name
    start_date = parsed_arguments.start_date
    end_date = parsed_arguments.end_date

    scores_text = read_scores_text(scores_file_name)
    try:
        score_master = ScoreMaster(scores_text, start_date, end_date)
    except ScoreMaster.BadLineException as exception:
        line_number = exception.line_number
        message = exception.message
        print(
            f'Error (`{scores_file_name}`, line {line_number}): {message}'
        )
        sys.exit(1)

    base_name = ''.join([
        scores_file_name,
        f' --from {start_date}' if start_date else '',
        f' --to {end_date}' if end_date else '',
    ])
    tsv_file_name = f'{base_name}.tsv'
    score_master.write_tsv(tsv_file_name)


if __name__ == '__main__':
    main()
