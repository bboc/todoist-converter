# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import codecs
from string import Template
from unicode_csv import UnicodeReader, UnicodeWriter
import xml.etree.cElementTree as ET

from common import target_name, title, row_to_dict, process_note
from const import AUTHOR, CONTENT, DATE, DATE_LANG, INDENT, PRIORITY, RESPONSIBLE, TYPE, FIELDNAMES
from const import TYPE_TASK, TYPE_NOTE


# OPML attribute for note
NOTE_ATTRIB = '_note'


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
