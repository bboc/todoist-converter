# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import argparse

from converters import CsvToMarkdownConverter, OpmlToCsvConverter, CsvToOpmlConverter
from taskpaper import CsvToTaskPaperConverter

FORMAT_MD = 'md'
FORMAT_OPML = 'opml'
FORMAT_CSV = 'todoist'
FORMAT_TASKPAPER = 'taskpaper'



def convert(args):
    """
    Convert file to specified format.
    Rows: TYPE (task, note),CONTENT,PRIORITY(1-4),INDENT,AUTHOR,RESPONSIBLE,DATE,DATE_LANG
    """

    if args.format.lower() == FORMAT_OPML:
        c = CsvToOpmlConverter(args)
    elif args.format.lower() == FORMAT_CSV:
        c = OpmlToCsvConverter(args)
    elif args.format.lower() == FORMAT_TASKPAPER:
        c = CsvToTaskPaperConverter(args)
    else: 
        c = CsvToMarkdownConverter(args)

    c.convert()


def main():
    parser = argparse.ArgumentParser(
        description='Convert todoist template files to other formats.')

    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='increase level of verbosity (repeat up to 3 times)')
    parser.add_argument('--format', '-f', default='md',
                        help='format of target file: md, opml, todoist')

    parser.add_argument('file',
                        help='file to convert')
    
    args = parser.parse_args()
    convert(args)
