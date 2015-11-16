# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import codecs
import json
import os.path
from string import Template
from unicode_csv import UnicodeReader, UnicodeWriter
import xml.etree.cElementTree as ET


# Todoist csv fields
TYPE = 'TYPE'
CONTENT = 'CONTENT'
PRIORITY = 'PRIORITY'
INDENT = 'INDENT'
AUTHOR = 'AUTHOR'
RESPONSIBLE = 'RESPONSIBLE'
DATE = 'DATE'
DATE_LANG = 'DATE_LANG'

# (ordered) list of fieldnames for Todoist CSV
FIELDNAMES = TYPE,CONTENT,PRIORITY,INDENT,AUTHOR,RESPONSIBLE,DATE,DATE_LANG

TYPE_TASK = 'task'
TYPE_NOTE = 'note'

FORMAT_MD = 'md'
FORMAT_OPML = 'opml'
FORMAT_CSV = 'todoist'

# OPML attribute for note
NOTE_ATTRIB = '_note'


def convert(args):
    """
    Convert file to specified format.
    Rows: TYPE (task, note),CONTENT,PRIORITY(1-4),INDENT,AUTHOR,RESPONSIBLE,DATE,DATE_LANG
    """

    if args.format.lower() == FORMAT_OPML:
        convert_csv_to_opml(args)
    elif args.format.lower() == FORMAT_CSV:
        convert_opml_to_csv(args)
    else: 
        convert_csv_to_md(args)


def title(filename):
    """Extract title from filename."""
    s = os.path.join(os.path.splitext(os.path.basename(filename))[0])
    if s[-4:].lower() == '.csv':
        return s[:-4]
    else:
        return s


def target_name(filename, ext):
    """Return target filename."""
    return '.'.join((os.path.splitext(os.path.basename(filename))[0], ext))


def row_to_dict(row):
    return dict(zip(FIELDNAMES,row))


def convert_csv_to_md(args):
    """Convert CSV to Markdown."""
    img = Template('![$name]($url)')
    ttl = Template('# $title\n')

    with codecs.open(target_name(args.file, 'md'), 'w+', 'utf-8') as target:
        print(ttl.substitute(title=title(args.file)), file=target)
        with codecs.open(args.file, 'r') as csvfile:
            reader = UnicodeReader(csvfile)
            for row in reader:
                row = row_to_dict(row)
                if row[TYPE] == TYPE_TASK:
                    print('#' * (int(row[INDENT])+1), row[CONTENT], '\n', file=target)
                elif row[TYPE] == TYPE_NOTE:
                    if row[CONTENT].strip().startswith(u'[[file'):
                        j = json.loads(row[CONTENT][8:-2])
                        print(img.substitute(name=j['file_name'], url=j['file_url']), '\n', file=target)
                    else:
                        print(row[CONTENT], '\n', file=target)
        print('\n', file=target)


def convert_csv_to_opml(args):
    """Convert Todoist CSV to OPML."""

    img = Template('Image "$name": $url')

    opml = ET.Element("opml", version='1.0')
    head = ET.SubElement(opml, 'head')
    ET.SubElement(head, 'title').text = title(args.file)
    ET.SubElement(head, 'expansionState').text = '0,1'
    body = ET.SubElement(opml, 'body')

    parents = {}
    parents[0] = body

    with codecs.open(args.file, 'r') as csvfile:
        reader = UnicodeReader(csvfile)
        for row in reader:
            row = row_to_dict(row)
            if row[TYPE] == TYPE_TASK:
                level = int(row[INDENT])
                current = ET.SubElement(parents[level-1], 'outline', text=row[CONTENT])
                parents[level] = current
            elif row[TYPE] == TYPE_NOTE:
                if row[CONTENT].strip().startswith(u'[[file'):
                    j = json.loads(row[CONTENT][8:-2])
                    new_note = img.substitute(name=j['file_name'], url=j['file_url'])
                else:
                    new_note = row[CONTENT]
                note = current.get(NOTE_ATTRIB)
                if note: 
                    current.set(NOTE_ATTRIB, '\n\n'.join((note, new_note)))
                else:
                    current.set(NOTE_ATTRIB, new_note)

    tree = ET.ElementTree(opml)
    tree.write(target_name(args.file, 'opml'), encoding='UTF-8', xml_declaration=True)


def convert_opml_to_csv(args):
    """Convert OPML file to Todoist CSV."""

    tree = ET.parse(args.file)
    opml = tree.getroot()
    body = opml.find('body')
    with codecs.open(target_name(args.file, 'csv'), 'w+') as target:
        writer = UnicodeWriter(target, FIELDNAMES)
        def make_row(type='', content='', indent = ''):
            return [type, content, '', indent, '', '', '', '']

        def process_element(outline, level=1):
            # content
            row = make_row(TYPE_TASK, outline.get('text'), str(level))
            writer.writerow(row)
            # note
            note = outline.get(NOTE_ATTRIB)
            if note:
                row = make_row(TYPE_NOTE, note)
                writer.writerow(row)
            # separator
            writer.writerow(make_row())
            for subelement in outline.findall('outline'):
                process_element(subelement, level+1)

        for outline in body:
            process_element(outline)


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
