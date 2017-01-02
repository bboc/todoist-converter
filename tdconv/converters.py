# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import codecs
from string import Template
from unicode_csv import UnicodeReader, UnicodeWriter
import xml.etree.cElementTree as ET

from common import Converter, Note
from const import AUTHOR, CONTENT, DATE, DATE_LANG, INDENT, PRIORITY, RESPONSIBLE, TYPE, FIELDNAMES
from const import TYPE_TASK, TYPE_NOTE


# OPML attribute for note
NOTE_ATTRIB = '_note'


def convert_csv_to_md(args):
    """Convert CSV to Markdown."""
    c = CsvToMarkdownConverter(args)
    c.convert()


class CsvToMarkdownConverter(Converter):

    def __init__(self, args):
        super(CsvToMarkdownConverter, self).__init__(args)

    def convert(self):
        att = Template('[$name]($url)')
        ttl = Template('# $title\n')

        with codecs.open(self.target_name(self.args.file, 'md'), 'w+', 'utf-8') as target:
            print(ttl.substitute(title=self.title(self.args.file)), file=target)
            with codecs.open(self.args.file, 'r') as csvfile:

                for row in map(self.Row._make, UnicodeReader(csvfile)):
                    if row.type == TYPE_TASK:
                        print('#' * (int(row.indent)+1), row.content, '\n', file=target)
                    elif row.type == TYPE_NOTE:
                        note = Note((row.content))
                        if note.text:
                            print(note.text, '\n', file=target)
                        if note.attachment:
                            print(att.substitute(name=note.attachment.name, url=note.attachment.url), '\n', file=target)
            print('\n', file=target)




def convert_csv_to_opml(args):
    """Convert Todoist CSV to OPML."""
    c = CsvToOpmlConverter(args)
    c.convert()


class CsvToOpmlConverter(Converter):

    def __init__(self, args):
        super(CsvToOpmlConverter, self).__init__(args)

    def convert(self):


        img = Template('Image "$name": $url')

        opml = ET.Element("opml", version='1.0')
        head = ET.SubElement(opml, 'head')
        ET.SubElement(head, 'title').text = self.title(self.args.file)
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

        with codecs.open(self.args.file, 'r') as csvfile:

            for row in map(self.Row._make, UnicodeReader(csvfile)):
                if row.type == TYPE_TASK:
                    level = int(row.indent)
                    current = ET.SubElement(parents[level-1], 'outline', text=row.content)
                    parents[level] = current
                elif row.type == TYPE_NOTE:
                    note = Note(row.content)
                    if note.attachment: 
                        opml_append_note(current, img.substitute(name=note.attachment.name, url=note.attachment.url))
                    if note.text:
                        opml_append_note(current, note.text)

        tree = ET.ElementTree(opml)
        tree.write(self.target_name(self.args.file, 'opml'), encoding='UTF-8', xml_declaration=True)


def convert_opml_to_csv(args):
    """Convert OPML file to Todoist CSV."""
    c = OpmlToCsvConverter(args)
    c.convert()


class OpmlToCsvConverter(Converter):

    def __init__(self, args):
        super(OpmlToCsvConverter, self).__init__(args)

    def convert(self):
        tree = ET.parse(self.args.file)
        opml = tree.getroot()
        body = opml.find('body')
        with codecs.open(self.target_name(self.args.file, 'csv'), 'w+') as target:
            self.writer = UnicodeWriter(target, FIELDNAMES)
            self.writer.writerow(FIELDNAMES)

            for outline in body:
                self.process_element(outline)

    def make_row(self, type='', content='', indent = ''):
        return [type, content, '', indent, '', '', '', '', '']

    def process_element(self, outline, level=1):
        # content
        row = self.make_row(TYPE_TASK, outline.get('text'), str(level))
        self.writer.writerow(row)
        # note
        note = outline.get(NOTE_ATTRIB)
        if note:
            row = self.make_row(TYPE_NOTE, note)
            self.writer.writerow(row)
        # separator
        self.writer.writerow(self.make_row())
        for subelement in outline.findall('outline'):
            self.process_element(subelement, level+1)


