# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple
import json
import os.path
import re
from string import Template
import urllib2

from const import AUTHOR, CONTENT, DATE, DATE_LANG, INDENT, PRIORITY, RESPONSIBLE, TYPE, FIELDNAMES
	

class Converter(object):

    TYPE_TASK = 'task'
    TYPE_NOTE = 'note'

    # OPML attribute for note
    NOTE_ATTRIB = '_note'

    def __init__(self, args):
        print( ', '.join(FIELDNAMES).lower())
        self.Row = namedtuple('Row', ', '.join(FIELDNAMES).lower())
        self.args = args
    
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


class Note(object):
    """
    A note may contain content, or an attachment, or both.
    The attachment is either None, or an Attachment object.
    """
    # pattern for attachments in notes
    NOTE = re.compile("(?P<text>.*?)\[\[file(?P<attachment>.*?)\]\]")

    def __init__(self, content):
        self.text = content
        self.attachment = None
        self._extract_content_and_attachment()
    
    def _extract_content_and_attachment(self):
        """Extract note text and attachment (if present)."""
        
        match = Note.NOTE.match(self.text)
        if match:
            j = json.loads(match.group('attachment'))
            self.text = match.group('text').strip()
            self.attachment = Attachment(j['file_name'], url=j['file_url'])


class Attachment(object):
    ATTACHMENTS_DIR = 'attachments'

    def __init__(self, filename, url):
        self.name = filename
        self.url = url

    def download(self):
        """Download attachment to attachments dir, make sure dir is created
        and handle filename collisions."""
        dirname=Attachment.ATTACHMENTS_DIR
        self._create_attachments_dir(dirname)
        relpath = self._find_filename(dirname, self.name)
        self._download_file(relpath)

    def _create_attachments_dir(self, dirname):
        """Create directory if it does not exist, if it exists make sure it's a directory and not a file."""
        if not(os.path.exists(dirname)):
            os.mkdir(dirname)
        if os.path.isfile(dirname):
            raise Exception(dirname, 'already exist as a file')

    def _download_file(filename):
        """Download a URL to filename."""
        f = urllib2.urlopen(self.url)
        with open(filename, "wb") as target:
            target.write(f.read())        

    def _find_filename(dirname):
        """Indentify (and return) a filename for the attachment: if filename is already taken,
        try <filename>(n>1).<ext> until file can be downloaded."""
        full_filename = os.path.join(dirname, self.filename)
        root, ext = os.path.splitext(self.filename)
        index = 1
        tpl = Template("$root($index)$ext")
        while os.path.exists(full_filename):
            index += 1 
            full_filename = os.path.join(dirname,tpl.substitute(root=root, index=index, ext=ext))
        return full_filename



