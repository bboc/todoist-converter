# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import codecs
import json
import os.path
import re
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
FORMAT_TASKPAPER = 'taskpaper'

# OPML attribute for note
NOTE_ATTRIB = '_note'

# pattern for attachments in notes
NOTE = re.compile("(?P<text>.*?)\[\[file(?P<attachment>.*?)\]\]")


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


def title(filename):
    """Extract title from filename."""
    s = os.path.join(os.path.splitext(os.path.basename(filename))[0])
    if s[-4:].lower() == '.csv':
        return s[:-4]
    else:
        return s

def target_name(filename, ext):
    """Return target filename."""
    try:
        return '.'.join((os.path.splitext(os.path.basename(filename))[0], ext))
    except UnicodeDecodeError:
        raise Exception("can't process filename", filename, ext)

def row_to_dict(row):
    return dict(zip(FIELDNAMES,row))

def process_note(content):
    """Extract note text and attachment (if present)."""

    match = NOTE.match(content)
    if match:
        j = json.loads(match.group('attachment'))
        return (match.group('text').strip(), # content
            dict(name=j['file_name'], url=j['file_url']))
    else:
        return  (content, None)


def convert_csv_to_md(args):
    """Convert CSV to Markdown."""
    att = Template('[$name]($url)')
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
                    text, attachment = process_note(row[CONTENT])
                    if text:
                        print(text, '\n', file=target)
                    if attachment:
                        print(att.substitute(name=attachment['name'], url=attachment['url']), '\n', file=target)
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

    def opml_append_note(current, contents):
        note = current.get(NOTE_ATTRIB)
        if note: 
            current.set(NOTE_ATTRIB, '\n\n'.join((note, contents)))
        else:
            current.set(NOTE_ATTRIB, contents)

    with codecs.open(args.file, 'r') as csvfile:
        reader = UnicodeReader(csvfile)
        for row in reader:
            row = row_to_dict(row)
            if row[TYPE] == TYPE_TASK:
                level = int(row[INDENT])
                current = ET.SubElement(parents[level-1], 'outline', text=row[CONTENT])
                parents[level] = current
            elif row[TYPE] == TYPE_NOTE:
                text, attachment = process_note(row[CONTENT])
                if attachment: 
                    opml_append_note(current, img.substitute(name=attachment['name'], url=attachment['url']))
                if text:
                    opml_append_note(current, text)

    tree = ET.ElementTree(opml)
    tree.write(target_name(args.file, 'opml'), encoding='UTF-8', xml_declaration=True)


TP_TASK = Template('$indent- $content')
TP_PROJECT = Template('$indent$content:')
TP_NOTE = Template('$indent$content')

def convert_csv_to_taskpaper(args):
    """Convert todoist project file to TaskPaper."""
    project = Template('$title:\n')
    indent = 1

    with codecs.open(target_name(args.file, 'taskpaper'), 'w+', 'utf-8') as target:
        # Add file name as top level project (all tasks belong to that project)
        print(project.substitute(title=title(args.file)), file=target)
        with codecs.open(args.file, 'r') as csvfile:
            reader = UnicodeReader(csvfile)
            for row in reader:
                row = row_to_dict(row)
                if row[TYPE] == TYPE_TASK:
                    indent = int(row[INDENT])
                    task_to_tp(row, target)
                elif row[TYPE] == TYPE_NOTE:
                    note_to_tp(row, target, indent)

        print('\n', file=target)

def task_to_tp(row, target):
    """Convert one task to TaskPaper."""
    content = row[CONTENT]
    # treat all 'unclickable' (sub-)tasks as projects
    if content.startswith('* '):
        tpl = TP_PROJECT
        content = content[2:]
    else:
        tpl = TP_TASK

    # add priority tag for prio 1-3:
    if int(row[PRIORITY]) < 4: 
        content = ''.join((content, ' @priority(%s)' % row[PRIORITY]))
    # add @due(date):
    if row[DATE]:
        content = ''.join((content, ' @due(%s)' % row[DATE]))
    
    # clean tags
    content = content.replace('@/', '@')
    print(tpl.substitute(indent = '\t' * (int(row[INDENT])), content=content), file=target)

def note_to_tp(row, target, indent):
    """Convert one note to TaskPaper."""
    text, attachment = process_note(row[CONTENT])
    tabs = '\t' * (indent + 1) # notes need an additional level of indentation
    if text:
        for line in text.split('\n'):
            print(TP_NOTE.substitute(indent=tabs, content=line), file=target)
    if attachment:
        content = ': '.join((attachment['name'], attachment['url']))
        print(TP_NOTE.substitute(indent=tabs, content=content), file=target)


def convert_opml_to_csv(args):
    """Convert OPML file to Todoist CSV."""

    tree = ET.parse(args.file)
    opml = tree.getroot()
    body = opml.find('body')
    with codecs.open(target_name(args.file, 'csv'), 'w+') as target:
        writer = UnicodeWriter(target, FIELDNAMES)
        writer.writerow(FIELDNAMES)
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
