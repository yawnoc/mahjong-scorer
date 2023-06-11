#!/usr/bin/env python3

"""
# mahjong.py

A Python scorer for Mahjong.

Copyright 2023 Conway
Licensed under MIT No Attribution (MIT-0), see LICENSE.
"""

import argparse
import os
import sys

__version__ = '0.0.0'


class ScoreMaster:
    def __init__(self, scores_text):
        self.players_including_everyone, self.games = ScoreMaster.parse(scores_text)

    @staticmethod
    def parse(scores_text):
        # TODO: actual implementation
        return None, None

    class BadLineException(Exception):
        def __int__(self, line_number, message):
            self.line_number = line_number
            self.message = message


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
