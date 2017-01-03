# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import codecs
from string import Template
from unicode_csv import UnicodeReader, UnicodeWriter

from common import Converter, Note


class CsvToTaskPaperConverter(Converter):
    TP_TASK = Template('$indent- $content')
    TP_PROJECT = Template('$indent$content:')
    TP_NOTE = Template('$indent$content')
    TP_TOP_PROJECT = Template('$title:')

    def __init__(self, args):
        super(CsvToTaskPaperConverter, self).__init__(args)

    def convert(self):
        self.indent = 1
        with codecs.open(self.target_name(self.args.file, 'taskpaper'), 'w+', 'utf-8') as self.target:
            # Add file name as top level project (all tasks belong to that project)
            self._print(self.TP_TOP_PROJECT.substitute(title=self.title(self.args.file)))
            
            super(CsvToTaskPaperConverter, self).convert()
            self._print('\n')
    
    def process_task(self, row):
        """Convert one task to TaskPaper."""
        self.indent = int(row.indent)
        content = row.content
        # treat all 'unclickable' (sub-)tasks as projects
        if content.startswith('* '):
            tpl = self.TP_PROJECT
            content = content[2:]
        else:
            tpl = self.TP_TASK

        # add priority tag for prio 1-3:
        if int(row.priority) < 4: 
            content = ''.join((content, ' @priority(%s)' % row.priority))
        # add @due(date):
        if row.date:
            content = ''.join((content, ' @due(%s)' % row.date))
        # clean tags
        content = content.replace('@/', '@')
        self._print(tpl.substitute(indent = '\t' * (int(row.indent)), content=content))


    def process_note(self, note):
        """Convert one note to TaskPaper."""
        tabs = '\t' * (self.indent + 1) # notes need an additional level of indentation
        if note.text:
            for line in note.text.split('\n'):
                self._print(self.TP_NOTE.substitute(indent=tabs, content=line))
        if note.attachment:
            content = ': '.join((note.attachment.name, note.attachment.url))
            ## content = tp_file(attachment['url'])
            self._print(self.TP_NOTE.substitute(indent=tabs, content=content))

    @staticmethod
    def tp_file(relpath):
        """Make relative TaskPaper file reference: prefix with ./ and escape spaces."""
        return ''.join(('./', relpath.replace(' ', '\ ')))

