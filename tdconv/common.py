# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import json
import os.path
import re
from string import Template
import urllib2

from const import AUTHOR, CONTENT, DATE, DATE_LANG, INDENT, PRIORITY, RESPONSIBLE, TYPE, FIELDNAMES
	

# pattern for attachments in notes
NOTE = re.compile("(?P<text>.*?)\[\[file(?P<attachment>.*?)\]\]")

ATTACHMENTS_DIR = 'attachments'


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
    """Extract note text and attachment (if present), download attachment to folder attachments."""

    def create_dir(dirname):
        """Create directory if it dies not exist, if it exists make sure it's a directory and not a file."""
        if os.path.exists(dirname):
            if os.path.isfile(dirname):
                raise Exception(dirname, 'already exist as a file')
            return
        os.mkdir(dirname)

    def download_file(url, filename):
        """Download a URL to filename."""
        f = urllib2.urlopen(url)
        with open(filename, "wb") as target:
            target.write(f.read())        

    def find_filename(dirname, filename):
        """Indentify (and return) a filename for the attachment: if filename is taken,
        try <filename>(n>1).<ext> until file can be downloaded."""
        full_filename = os.path.join(dirname, filename)
        root, ext = os.path.splitext(filename)
        index = 1
        tpl = Template("$root($index)$ext")
        while os.path.exists(full_filename):
            index += 1 
            full_filename = os.path.join(dirname,tpl.substitute(root=root, index=index, ext=ext))
        return full_filename


    match = NOTE.match(content)
    if match:
        ##create_dir(ATTACHMENTS_DIR)
        j = json.loads(match.group('attachment'))
        ## relpath = find_filename(ATTACHMENTS_DIR, j['file_name'])
        ## download_file(j['file_url'], relpath)
        return (match.group('text').strip(), # content
                dict(name=j['file_name'], url=j['file_url']))
    else:
        return (content, None)

