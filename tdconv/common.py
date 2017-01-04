# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import codecs
from collections import namedtuple
import os.path
import re
import urllib2
import zipfile

from const import FIELDNAMES
from unicode_csv import UnicodeReader

from note import Note

class Converter(object):

    TYPE_TASK = 'task'
    TYPE_NOTE = 'note'

    TITLE = re.compile("(?P<title>.*?) \[[0-9]{5,14}\]")

    def __init__(self, args):
        self.Row = namedtuple('Row', ', '.join(FIELDNAMES).lower())
        self.source_name = args.file
        self.target_name = self.make_target_name(self.source_name)
    
    @staticmethod
    def title(filename):
        """Extract title from filename. Remove Todoist Id"""
        # strip path and extension
        s = os.path.splitext(os.path.basename(filename))[0]
        match = Converter.TITLE.match(s)
        if match:
            return match.group('title')
        return s

    def make_target_name(self, filename, ext=None):
        """Return target filename."""
        if not ext:
            ext = self.EXT
        try:
            return '.'.join((os.path.splitext(os.path.basename(filename))[0], ext))
        except UnicodeDecodeError:
            raise Exception("can't process filename", filename, ext)

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


class Downloadable(object):
    def __init__(self, args):
        super(Downloadable, self).__init__(args)
        self.download_attachments = args.download



class ZipProcessor(object):

    def convert(self):
        if os.path.splitext(self.source_name)[1].lower() == '.zip':
            with ZipFile('spam.zip', 'w') as myzip:
                print(repr(myzip.infolist()))
