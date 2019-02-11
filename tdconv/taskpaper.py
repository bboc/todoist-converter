# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import codecs
from string import Template
from unicode_csv import UnicodeReader, UnicodeWriter

from common import Converter, Downloadable


class CsvToTaskPaperConverter(Downloadable, Converter):
    TP_TASK = Template('$indent- $content')
    TP_PROJECT = Template('$indent$content:')
    TP_NOTE = Template('$indent$content')
    TP_TOP_PROJECT = Template('$title:')
    TP_UNCLICABLE_TASK_PREFIX = '* '
    EXT = 'taskpaper'

    def convert(self):
        self.indent = 1
        with codecs.open(self.target_name, 'a+', 'utf-8') as self.target:
            # Add file name as top level project (all tasks belong to that project)
            self._print(self.TP_TOP_PROJECT.substitute(title=self.title(self.source_name)))
            super(CsvToTaskPaperConverter, self).convert()
            self._print('\n')

    def process_task(self, row):
        """Convert one task to TaskPaper."""
        content = row.content
        # treat 'unclickable' (sub-)tasks as projects
        if content.startswith(self.TP_UNCLICABLE_TASK_PREFIX):
            tpl = self.TP_PROJECT
            content = content[2:]
        else:
            tpl = self.TP_TASK

        content = self._add_priority(row, content)
        content = self._add_due_date(row, content)
        content = self._clean_tags(row, content)
        self.indent = int(row.indent)
        self._print(tpl.substitute(indent='\t' * (int(row.indent)), content=content))

    def _add_priority(self, row, content):
        """Add priority tag for prio 1-3."""
        if row.priority != '' and int(row.priority) < 4:
            content = ''.join((content, ' @priority(%s)' % row.priority))
        return content

    def _add_due_date(self, row, content):
        """Add @due(date)."""
        if row.date:
            content = ''.join((content, ' @due(%s)' % row.date))
        return content

    def _clean_tags(self, row, content):
        """Taskpaper does not like tags starting with '@/'."""
        return content.replace('@/', '@')

    def process_note(self, note):
        """Convert one note to TaskPaper."""
        tabs = '\t' * (self.indent + 1)  # notes need an additional level of indentation
        self._process_note_text(note.text, tabs)
        self._process_note_attachment(note.attachment, tabs)

    def _process_note_text(self, text, tabs):
        if text:
            for line in text.split('\n'):
                self._print(self.TP_NOTE.substitute(indent=tabs, content=line))

    def _process_note_attachment(self, attachment, tabs):
        if attachment:
            if self.download_attachments:
                relpath = attachment.download()
                content = self.tp_file(relpath)
            else:
                content = ': '.join((attachment.name, attachment.url))
            self._print(self.TP_NOTE.substitute(indent=tabs, content=content))

    @staticmethod
    def tp_file(relpath):
        """Make relative TaskPaper file reference: prefix with ./ and escape spaces."""
        return ''.join(('./', relpath.replace(' ', '\ ')))
