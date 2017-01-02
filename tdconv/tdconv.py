# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import argparse

from common import target_name, title, row_to_dict, process_note
from converters import convert_csv_to_opml, convert_csv_to_md, convert_opml_to_csv
from taskpaper import convert_csv_to_taskpaper

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
        convert_csv_to_opml(args)
    elif args.format.lower() == FORMAT_CSV:
        convert_opml_to_csv(args)
    elif args.format.lower() == FORMAT_TASKPAPER:
        convert_csv_to_taskpaper(args)
    else: 
        convert_csv_to_md(args)




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
