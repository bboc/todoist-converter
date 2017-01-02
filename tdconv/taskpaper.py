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

    def __init__(self, args):
        super(CsvToTaskPaperConverter, self).__init__(args)

    def convert(self):
        TP_PROJECT = Template('$title:')
        indent = 1

        with codecs.open(self.target_name(self.args.file, 'taskpaper'), 'w+', 'utf-8') as target:
            # Add file name as top level project (all tasks belong to that project)
            print(TP_PROJECT.substitute(title=self.title(self.args.file)), file=target)
            with codecs.open(self.args.file, 'r') as csvfile:
                for row in map(self.Row._make, UnicodeReader(csvfile)):
                    if row.type == self.TYPE_TASK:
                        indent = int(row.indent)
                        self.task_to_tp(row, target)
                    elif row.type == self.TYPE_NOTE:
                        self.note_to_tp(row, target, indent)
            print('\n', file=target)

    def task_to_tp(self, row, target):
        """Convert one task to TaskPaper."""
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
        print(tpl.substitute(indent = '\t' * (int(row.indent)), content=content), file=target)

    def note_to_tp(self, row, target, indent):
        """Convert one note to TaskPaper."""
        note = Note(row.content)
        tabs = '\t' * (indent + 1) # notes need an additional level of indentation
        if note.text:
            for line in note.text.split('\n'):
                print(self.TP_NOTE.substitute(indent=tabs, content=line), file=target)
        if note.attachment:
            content = ': '.join((note.attachment.name, note.attachment.url))
            ## content = tp_file(attachment['url'])
            print(self.TP_NOTE.substitute(indent=tabs, content=content), file=target)

    @staticmethod
    def tp_file(relpath):
        """Make relative TaskPaper file reference: prefix with ./ and escape spaces."""
        return ''.join(('./', relpath.replace(' ', '\ ')))

