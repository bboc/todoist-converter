
from __future__ import print_function

import argparse
import csv
import json
import os.path
from string import Template
import xml.etree.cElementTree as ET

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
        convert_to_opml(args)
    else: 
        convert_to_md(args)


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


def convert_to_md(args):
    img = Template('\n![$name]($url)')

    print('#', title(args.file), '\n')

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


def convert_to_opml(args):

    img = Template('Image "$name": $url')
    NOTE = '_note'

    opml = ET.Element("opml", version='1.0')
    head = ET.SubElement(opml, 'head')
    ET.SubElement(head, 'title').text = title(args.file)
    ET.SubElement(head, 'expansionState').text = '0,1'
    body = ET.SubElement(opml, 'body')

    parents = {}
    parents[0] = body

    with open(args.file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row[TYPE] == 'task':
                level = int(row[INDENT])
                current = ET.SubElement(parents[level-1], 'outline', text=row[CONTENT])
                parents[level] = current
            elif row[TYPE] == 'note':
                if row[CONTENT].strip().startswith(u'[[file'):
                    j = json.loads(row[CONTENT][8:-2])
                    new_note = img.substitute(name=j['file_name'], url=j['file_url'])
                else:
                    new_note = row[CONTENT]
                note = current.get(NOTE)
                if note: 
                    current.set(NOTE, '\n\n'.join((note, new_note)))
                else:
                    current.set(NOTE, new_note)

    tree = ET.ElementTree(opml)
    tree.write(target_name(args.file, 'opml'), encoding='UTF-8', xml_declaration=True)


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
