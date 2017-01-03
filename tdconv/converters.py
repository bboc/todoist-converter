# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import codecs
from string import Template
from unicode_csv import UnicodeReader, UnicodeWriter
import xml.etree.cElementTree as ET

from common import Converter, Note
from const import FIELDNAMES

class CsvToMarkdownConverter(Converter):
    """Convert CSV to Markdown."""

    ATTACHMENT_LINK = Template('[$name]($url)')
    TITLE = Template('# $title\n')

    def __init__(self, args):
        super(CsvToMarkdownConverter, self).__init__(args)

    def convert(self):
        with codecs.open(self.target_name(self.args.file, 'md'), 'w+', 'utf-8') as self.target:
            self._print(self.TITLE.substitute(title=self.title(self.args.file)))
            super(CsvToMarkdownConverter, self).convert()
            self._print('\n')
    
    def process_task(self, row):
        self._print('#' * (int(row.indent)+1), row.content, '\n')

    def process_note(self, note):
        if note.text:
            self._print(note.text, '\n')
        if note.attachment:
            self._print(self.ATTACHMENT_LINK.substitute(name=note.attachment.name, url=note.attachment.url), '\n')


class CsvToOpmlConverter(Converter):
    """Convert Todoist CSV to OPML."""
    OPML_IMAGE = Template('Image "$name": $url')

    def __init__(self, args):
        super(CsvToOpmlConverter, self).__init__(args)

    def convert(self):

        opml = ET.Element("opml", version='1.0')
        head = ET.SubElement(opml, 'head')
        ET.SubElement(head, 'title').text = self.title(self.args.file)
        ET.SubElement(head, 'expansionState').text = '0,1'
        body = ET.SubElement(opml, 'body')

        self.parents = {}
        self.parents[0] = body

        super(CsvToOpmlConverter, self).convert()
        tree = ET.ElementTree(opml)
        tree.write(self.target_name(self.args.file, 'opml'), encoding='UTF-8', xml_declaration=True)

    def process_task(self, row):
        level = int(row.indent)
        self.current = ET.SubElement(self.parents[level-1], 'outline', text=row.content)
        self.parents[level] = self.current

    def process_note(self, note):
        if note.attachment: 
            self.opml_append_note(self.OPML_IMAGE.substitute(name=note.attachment.name, url=note.attachment.url))
        if note.text:
            self.opml_append_note(note.text)

    def opml_append_note(self, contents):
        note = self.current.get(self.NOTE_ATTRIB)
        if note: 
            self.current.set(self.NOTE_ATTRIB, '\n\n'.join((note, contents)))
        else:
            self.current.set(self.NOTE_ATTRIB, contents)


class OpmlToCsvConverter(Converter):
    """Convert OPML file to Todoist CSV."""

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
        row = self.make_row(self.TYPE_TASK, outline.get('text'), str(level))
        self.writer.writerow(row)
        # note
        note = outline.get(self.NOTE_ATTRIB)
        if note:
            row = self.make_row(self.TYPE_NOTE, note)
            self.writer.writerow(row)
        # separator
        self.writer.writerow(self.make_row())
        for subelement in outline.findall('outline'):
            self.process_element(subelement, level+1)


