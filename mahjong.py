#!/usr/bin/env python3

"""
# mahjong.py

A Python scorer for Mahjong.

Copyright 2023 Conway
Licensed under MIT No Attribution (MIT-0), see LICENSE.
"""

import argparse
import os
import re
import sys

__version__ = '0.0.0'
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

    @staticmethod
    def parse(scores_text):
        player_from_name = {}
        games = []

        date = None
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
                # TODO: NoPlayersException
                # TODO: scoring logic
                continue

            if ScoreMaster.match_comment_line(line):
                continue

            # TODO: InvalidLineException

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
        raise NotImplementedError

    @staticmethod
    def match_comment_line(line):
        return re.fullmatch(
            pattern=r'^ [\s]* (?: [#] .* )? $',
            string=line,
            flags=re.VERBOSE,
        )

    class BadLineException(Exception):
        def __int__(self, line_number, message):
            self.line_number = line_number
            self.message = message

    class DuplicatePlayerNamesException(BadLineException):
        pass


class Player:
    def __init__(self, name):
        self.name = name

        # TODO: scoring fields


def parse_command_line_arguments():
    argument_parser = argparse.ArgumentParser(
        description='Score some games of Mahjong.'
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
