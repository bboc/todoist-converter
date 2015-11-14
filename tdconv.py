
from __future__ import print_function

import argparse
import csv
import json
from string import Template

CONTENT = 'CONTENT'
INDENT = 'INDENT'
PRIORITY = 'PRIORITY'
TYPE = 'TYPE'


def convert(args):
    """
    Convert file to specified format.
    Rows: TYPE (task, note),CONTENT,PRIORITY(1-4),INDENT,AUTHOR,RESPONSIBLE,DATE,DATE_LANG
    """

    if args.format == 'opml':
        print('OPML format not implemented yet')
    else: 
        convert_to_md(args)

def convert_to_md(args):
    img = Template('\n![$name]($url)')

    if args.file[-4:].lower() == '.csv':
        headline = args.file[:-4]
    else:
        headline = args.file
    print('#', headline, '\n')

    with open(args.file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row[TYPE] == 'task':
                print('#' * (int(row[INDENT])+1), row[CONTENT], '\n')
            elif row[TYPE] == 'note':
                if row[CONTENT].strip().startswith(u'[[file'):
                    j = json.loads(row[CONTENT][8:-2])
                    print(img.substitute(name=j['file_name'], url=j['file_url']), '\n')
                else:
                    print(row[CONTENT], '\n')
    print('\n')


def main():
    parser = argparse.ArgumentParser(
        description='Convert todoist template files to other formats.')

    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='increase level of verbosity (repeat up to 3 times)')
    parser.add_argument('--format', '-f', default='md',
                        help='format of target file: md (later maybe also opml')

    parser.add_argument('file',
                        help='file to convert')
    
    args = parser.parse_args()
    convert(args)
