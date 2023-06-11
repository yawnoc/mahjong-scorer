#!/usr/bin/env python3

"""
# mahjong.py

A Python scorer for Mahjong (HK rules).

Copyright 2023 Conway
Licensed under MIT No Attribution (MIT-0), see LICENSE.
"""

import argparse
import os
import re
import sys

__version__ = '0.0.0'
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


class ScoreMaster:
    def __init__(self, scores_text):
        self.players_including_everyone, self.games = ScoreMaster.parse(scores_text)

    LINE_EXPLAINER = (
        f'A line must have one of the following forms:\n'
        f'    <yyyy>-<mm>-<dd>     # a date\n'
        f'    B=<base>             # a declaration of base points (default {DEFAULT_BASE})\n'
        f'    M=<faan>             # a declaration of maximum faan (default {DEFAULT_MAXIMUM_FAAN})\n'
        f'    R=half | full        # a declaration of responsibility (default {DEFAULT_RESPONSIBILITY})\n'
        f'                         #   half  = half responsibility (半銃)\n'
        f'                         #   full  = full responsibility (全銃)\n'
        f'    S=half | spicy       # a declaration of spiciness (default {DEFAULT_SPICINESS})\n'
        f'                         #   half  = half-spicy rise (半辣上)\n'
        f'                         #   spicy = spicy-spicy rise (辣辣上)\n'
        f'    <P1> <P2> <P3> <P4>  # a list of player names (no hashes, asterisks, or\n'
        f'                         # leading digits)\n'
        f'    <R1> <R2> <R3> <R4>  # a declaration of game results\n'
        f"                         #   <digits> = winner's faan\n"
        f'                         #   -        = blameless player\n'
        f'                         #   d        = discarding (打出) player\n'
        f'                         #   g        = guaranteeing (包自摸) player\n'
        f'                         #   f        = false-winning (詐糊) player\n'
        f'    # <comment>          # a comment, also allowed at the end of the forms\n'
        f'                         # above\n'
        f'All other lines are invalid.\n'
    )

    @staticmethod
    def parse(scores_text):
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
                date = date_line_match.group('date')
                continue

            base_line_match = ScoreMaster.match_base_line(line)
            if base_line_match:
                base = int(base_line_match.group('base'))
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

                faan_strings = tuple(
                    game_line_match.group(f'faan_{i}')
                    for i in range(0, 4)
                )
                faan_indices = set(i for i in range(0, 4) if faan_strings[i])
                if len(faan_indices) > 1:
                    raise ScoreMaster.MultipleWinnersException(
                        line_number,
                        f'game declared with multiple winners (digits)',
                    )

                winner_index = faan_indices.pop()
                winner_faan = int(faan_strings[winner_index])

                # TODO: scoring logic
                continue

            if ScoreMaster.match_comment_line(line):
                continue

            raise ScoreMaster.InvalidLineException(
                line_number,
                f'invalid line\n\n{ScoreMaster.LINE_EXPLAINER}',
            )

        for game in games:
            pass  # TODO: apply update to player

        players = list(player_from_name.values())
        everyone = Player('*')
        # TODO: everyone logic

        players_including_everyone = players + [everyone]

        total_game_count = len(games)
        for player in players_including_everyone:
            pass  # TODO: apply update of averages

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
                B=(?P<base> [0-9]+ )
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
        player_name_regex = r'[^\s#*0-9][^\s#*]*'
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
        loss_regex = '[-dgf]'  # null, discard, guarantee, or false-win
        return re.fullmatch(
            pattern=fr'''
                ^ [\s]*
                (?: (?P<faan_0> {faan_regex} ) | (?P<loss_0> {loss_regex} )  )
                    [\s]+
                (?: (?P<faan_1> {faan_regex} ) | (?P<loss_1> {loss_regex} )  )
                    [\s]+
                (?: (?P<faan_2> {faan_regex} ) | (?P<loss_2> {loss_regex} )  )
                    [\s]+
                (?: (?P<faan_3> {faan_regex} ) | (?P<loss_3> {loss_regex} )  )
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

    class BadLineException(Exception):
        def __init__(self, line_number, message):
            self.line_number = line_number
            self.message = message

    class DuplicatePlayerNamesException(BadLineException):
        pass

    class NoPlayersException(BadLineException):
        pass

    class InvalidLineException(BadLineException):
        pass

    class MultipleWinnersException(BadLineException):
        pass


class Player:
    def __init__(self, name):
        self.name = name

        # TODO: scoring fields


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

    scores_text = read_scores_text(scores_file_name)
    try:
        score_master = ScoreMaster(scores_text)
    except ScoreMaster.BadLineException as exception:
        line_number = exception.line_number
        message = exception.message
        print(
            f'Error (`{scores_file_name}`, line {line_number}): {message}'
        )
        sys.exit(1)


if __name__ == '__main__':
    main()
