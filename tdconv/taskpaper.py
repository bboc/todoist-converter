# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals


import codecs
from string import Template
from unicode_csv import UnicodeReader, UnicodeWriter


from const import AUTHOR, CONTENT, DATE, DATE_LANG, INDENT, PRIORITY, RESPONSIBLE, TYPE
from const import TYPE_TASK, TYPE_NOTE

from common import target_name, title, row_to_dict, process_note

TP_TASK = Template('$indent- $content')
TP_PROJECT = Template('$indent$content:')
TP_NOTE = Template('$indent$content')

def convert_csv_to_taskpaper(args):
    """Convert todoist project file to TaskPaper."""
    TP_PROJECT = Template('$title:')
    indent = 1

    with codecs.open(target_name(args.file, 'taskpaper'), 'w+', 'utf-8') as target:
        # Add file name as top level project (all tasks belong to that project)
        print(TP_PROJECT.substitute(title=title(args.file)), file=target)
        with codecs.open(args.file, 'r') as csvfile:
            reader = UnicodeReader(csvfile)
            for row in reader:
                row = row_to_dict(row)
                if row[TYPE] == TYPE_TASK:
                    indent = int(row[INDENT])
                    task_to_tp(row, target)
                elif row[TYPE] == TYPE_NOTE:
                    note_to_tp(row, target, indent)

        print('\n', file=target)

def task_to_tp(row, target):
    """Convert one task to TaskPaper."""
    content = row[CONTENT]
    # treat all 'unclickable' (sub-)tasks as projects
    if content.startswith('* '):
        tpl = TP_PROJECT
        content = content[2:]
    else:
        tpl = TP_TASK

    # add priority tag for prio 1-3:
    if int(row[PRIORITY]) < 4: 
        content = ''.join((content, ' @priority(%s)' % row[PRIORITY]))
    # add @due(date):
    if row[DATE]:
        content = ''.join((content, ' @due(%s)' % row[DATE]))
    # clean tags
    content = content.replace('@/', '@')
    print(tpl.substitute(indent = '\t' * (int(row[INDENT])), content=content), file=target)

def note_to_tp(row, target, indent):
    """Convert one note to TaskPaper."""
    text, attachment = process_note(row[CONTENT])
    tabs = '\t' * (indent + 1) # notes need an additional level of indentation
    if text:
        for line in text.split('\n'):
            print(TP_NOTE.substitute(indent=tabs, content=line), file=target)
    if attachment:
        content = ': '.join((attachment['name'], attachment['url']))
        ## content = tp_file(attachment['url'])
        print(TP_NOTE.substitute(indent=tabs, content=content), file=target)


def tp_file(relpath):
    """Make relative TaskPaper file reference: prefix with ./ and escape spaces."""
    return ''.join(('./', relpath.replace(' ', '\ ')))

