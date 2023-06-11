#!/usr/bin/env python3

"""
# mahjong.py

A Python scorer for Mahjong.

Copyright 2023 Conway
Licensed under MIT No Attribution (MIT-0), see LICENSE.
"""

import argparse

__version__ = '0.0.0'


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


def main():
    parsed_arguments = parse_command_line_arguments()
    scores_file_name = parsed_arguments.scores_file_name


if __name__ == '__main__':
    main()
