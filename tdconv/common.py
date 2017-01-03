# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import codecs
from collections import namedtuple
import os.path
import urllib2

from const import FIELDNAMES
from unicode_csv import UnicodeReader

from note import Note

class Converter(object):

    TYPE_TASK = 'task'
    TYPE_NOTE = 'note'

    # OPML attribute for note
    NOTE_ATTRIB = '_note'

    def __init__(self, args):
        self.Row = namedtuple('Row', ', '.join(FIELDNAMES).lower())
        self.source_name = args.file
    
    @staticmethod
    def title(filename):
        """Extract title from filename."""
        s = os.path.join(os.path.splitext(os.path.basename(filename))[0])
        if s[-4:].lower() == '.csv':
            return s[:-4]
        else:
            return s

    @staticmethod
    def target_name(filename, ext):
        """Return target filename."""
        try:
            return '.'.join((os.path.splitext(os.path.basename(filename))[0], ext))
        except UnicodeDecodeError:
            raise Exception("can't process filename", filename, ext)

    @staticmethod
    def row_to_dict(row):
        return dict(zip(FIELDNAMES,row))

    def convert(self):
        """
        Should be overridden in subclasses. Subclasses need to implement 
        process_task(row) and process_note(note).
        """
        with codecs.open(self.source_name, 'r') as csvfile:
            for row in map(self.Row._make, UnicodeReader(csvfile)):
                if row.type == self.TYPE_TASK:
                    self.process_task(row)
                elif row.type == self.TYPE_NOTE:
                    note = Note(row.content)
                    self.process_note(note)

    def _print(self, *msg):
        print(*msg, file=self.target)


