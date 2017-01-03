# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import codecs
from string import Template

from common import Converter

class CsvToMarkdownConverter(Converter):
    """Convert CSV to Markdown."""

    ATTACHMENT_LINK = Template('[$name]($url)')
    TITLE = Template('# $title\n')

    def __init__(self, args):
        super(CsvToMarkdownConverter, self).__init__(args)

    def convert(self):
        with codecs.open(self.target_name(self.source_name, 'md'), 'w+', 'utf-8') as self.target:
            self._print(self.TITLE.substitute(title=self.title(self.source_name)))
            super(CsvToMarkdownConverter, self).convert()
            self._print('\n')
    
    def process_task(self, row):
        self._print('#' * (int(row.indent)+1), row.content, '\n')

    def process_note(self, note):
        if note.text:
            self._print(note.text, '\n')
        if note.attachment:
            self._print(self.ATTACHMENT_LINK.substitute(name=note.attachment.name, url=note.attachment.url), '\n')
