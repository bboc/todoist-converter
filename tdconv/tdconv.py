# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import codecs
import logging
from textwrap import dedent
import zipfile
import os
from markdown import CsvToMarkdownConverter
from opml import OpmlToCsvConverter, CsvToOpmlConverter
from taskpaper import CsvToTaskPaperConverter

logger = logging.getLogger("tdconv")

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
        klass = CsvToOpmlConverter
    elif args.format.lower() == FORMAT_CSV:
        klass = OpmlToCsvConverter
    elif args.format.lower() == FORMAT_TASKPAPER:
        klass = CsvToTaskPaperConverter
    else:
        klass = CsvToMarkdownConverter

    if os.path.splitext(args.file)[1].lower() == '.zip':
        process_zip(klass, args)
    else:
        with codecs.open(args.file, 'r') as source_file:
            if args.output:
                target = args.output
            else:
                target = ''
            converter = klass(args, source_file, target)
            converter.convert()


def process_zip(converter_class, args):
    """convert all files in a zip file."""
    zip_path = args.file
    source_directory = os.path.split(zip_path)[0]
    print(source_directory)
    print(zip_path)
    target_extension = args.format
    if target_extension == 'todoist':
        target_extension == 'csv'
    with zipfile.ZipFile(zip_path, 'r') as archive:
        for info in archive.infolist():
            if info.filename.lower().endswith('.csv'):
                # limit processing to CSV-files
                logger.debug(info.filename)
                print(info.filename, repr(info))
                target_filename = make_target_filename(source_directory, info.filename, target_extension)
                print(target_filename)
                source_file = archive.open(info, 'r')
                converter = converter_class(args, source_file, target_filename)
                converter.convert()


def make_target_filename(directory, source_filename, target_extension):

    src_name = os.path.split(source_filename)[1]
    root = os.path.splitext(src_name)[0]
    return os.path.join(directory, '.'.join((root, target_extension)))


class TargetDirectoryDoesNotExistError(Exception):
    pass


def determine_target_directory(source_dir, output):
    if output:
        if output.startswith(os.sep):
            target = output
        else:
            target = os.path.join(source_dir, output)
        if not os.path.isdir(target):
            raise TargetDirectoryDoesNotExistError("Output dir '%s' does not exist" % target)
        return target
    return source_dir


def main():
    parser = argparse.ArgumentParser(
        description=dedent("""Convert Todoist template files (and Todoist backups) to other formats.
            To convert an entire backup use
            ls -bp | xargs -I xx tdconv -df taskpaper "xx"
            """))

    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='increase level of verbosity (repeat up to 3 times)')
    parser.add_argument('--format', '-f', default='md',
                        help='format of target file: md, opml, todoist, taskpaper')
    parser.add_argument('--output', '-o', default=None,
                        help='name of target file, if this argument is not present, name of source file will be used')
    parser.add_argument('--download', '-d', action="store_true", default=False,
                        help='download attachments')
    parser.add_argument('file',
                        help='file to convert (either csv, opml or a zip file that contains csv files')

    args = parser.parse_args()
    convert(args)
