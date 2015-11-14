
from __future__ import print_function

import argparse
import csv


def convert(args):
    """
    Convert file to specified format.
    Rows: TYPE (task, note),CONTENT,PRIORITY(1-4),INDENT,AUTHOR,RESPONSIBLE,DATE,DATE_LANG
    """
    TYPE = 'TYPE'
    PRIORITY = 'PRIORITY'
    CONTENT = 'CONTENT'
    INDENT = 'INDENT'

    with open(args.file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row[TYPE] == 'task':
                print('\n', '#' * int(row[INDENT]), row[CONTENT])
            elif row[TYPE] == 'note':
                print ('\n', row[CONTENT])


def main():
    parser = argparse.ArgumentParser(
        description='Convert todoist template files to other formats.')

    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='increase level of verbosity (repeat up to 3 times)')
    parser.add_argument('--format', '-f', default='md',
                        help='format of target file: md (later maybe also OPML')

    parser.add_argument('file',
                        help='file to convert')
    
    args = parser.parse_args()
    convert(args)
