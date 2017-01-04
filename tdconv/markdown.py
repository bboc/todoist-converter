# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import codecs
from string import Template

from common import Converter, Downloadable


class CsvToMarkdownConverter(Downloadable, Converter):
    """Convert CSV to Markdown."""

    ATTACHMENT_LINK = Template('[$name]($url)')
    IMAGE_LINK = Template('![$name]($url)')
    IMAGE_EXT = ['.jpg', '.jpeg', '.png', '.gif']
    TITLE = Template('# $title\n')
    EXT = 'md'

    def convert(self):
        with codecs.open(self.target_name, 'a+', 'utf-8') as self.target:
            self._print(self.TITLE.substitute(title=self.title(self.source_name)))
            super(CsvToMarkdownConverter, self).convert()
            self._print('\n')
    
    def process_task(self, row):
        self._print('#' * (int(row.indent)+1), row.content, '\n')

    def process_note(self, note):
        if note.text:
            self._print(note.text, '\n')
        self._process_note_attachment(note.attachment)


    def _process_note_attachment(self, attachment):
        if attachment:
            if self.download_attachments:
                url = attachment.download()
            else:
                url = attachment.url
            self._attachment_reference(attachment.name, url)
    
    def _attachment_reference(self, name, url):
        """
        Determine if attachment is an image, if so, create image reference,
        otherwise create a link.
        """
        tpl = self.ATTACHMENT_LINK
        for ext in self.IMAGE_EXT:
            if url.lower().endswith(ext):
                tpl = self.IMAGE_LINK
        url = url.replace(' ', '%20')
        self._print(tpl.substitute(name=name, url=url), '\n')
