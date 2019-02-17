# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import codecs
from string import Template
from unicode_csv import UnicodeWriter
import xml.etree.cElementTree as ET

from common import Converter
from const import FIELDNAMES


class OpmlConverter(Converter):
    # OPML attribute for note
    NOTE_ATTRIB = '_note'


class CsvToOpmlConverter(OpmlConverter):
    """Convert Todoist CSV to OPML."""
    OPML_IMAGE = Template('Image "$name": $url')
    EXT = 'opml'

    def __init__(self, cmd_args, *args, **kwargs):
        super(CsvToOpmlConverter, self).__init__(cmd_args, *args, **kwargs)

    def convert(self):
        opml, self.parents = self._prepare_document()
        super(CsvToOpmlConverter, self).convert()
        tree = ET.ElementTree(opml)
        tree.write(self.target_name, encoding='UTF-8', xml_declaration=True)

    def _prepare_document(self):
        opml = ET.Element("opml", version='1.0')
        head = ET.SubElement(opml, 'head')
        ET.SubElement(head, 'title').text = self.title(self.source_name)
        ET.SubElement(head, 'expansionState').text = '0,1'
        body = ET.SubElement(opml, 'body')
        parents = {}
        parents[0] = body
        return opml, parents

    def process_task(self, row):
        level = int(row.indent)
        self.current = ET.SubElement(self.parents[level - 1], 'outline', text=row.content)
        self.parents[level] = self.current

    def process_note(self, note):
        if note.text:
            self._opml_append_note(note.text)
        if note.attachment:
            self._opml_append_note(self.OPML_IMAGE.substitute(name=note.attachment.name, url=note.attachment.url))

    def _opml_append_note(self, contents):
        note = self.current.get(self.NOTE_ATTRIB)
        if note:
            self.current.set(self.NOTE_ATTRIB, '\n\n'.join((note, contents)))
        else:
            self.current.set(self.NOTE_ATTRIB, contents)


class OpmlToCsvConverter(OpmlConverter):
    """Convert OPML file to Todoist CSV."""
    EXT = 'csv'

    def __init__(self, cmd_args, *args, **kwargs):
        super(OpmlToCsvConverter, self).__init__(cmd_args, *args, **kwargs)

    def convert(self):
        document_body = self._prepare_document()
        with codecs.open(self.target_name, 'w+') as target:
            self.writer = UnicodeWriter(target, FIELDNAMES)
            self._write_header_row()
            for outline in document_body:
                self.process_element(outline)

    def _prepare_document(self):
        # TODO: add zipfile support here
        tree = ET.parse(self.source_name)
        opml = tree.getroot()
        return opml.find('body')

    def _write_header_row(self):
        self.writer.writerow(FIELDNAMES)

    def _make_row(self, type='', content='', indent=''):
        return [type, content, '', indent, '', '', '', '', '']

    def process_element(self, outline, level=1):
        # content
        row = self._make_row(self.TYPE_TASK, outline.get('text'), str(level))
        self.writer.writerow(row)
        # note
        note = outline.get(self.NOTE_ATTRIB)
        if note:
            row = self._make_row(self.TYPE_NOTE, note)
            self.writer.writerow(row)
        # separator
        self.writer.writerow(self._make_row())
        for subelement in outline.findall('outline'):
            self.process_element(subelement, level + 1)
