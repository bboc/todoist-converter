# -*- coding: utf-8 -*-
"""
Tkinter wrapper for tdconv.

Note: When building a native app with pyinstaller, the working directory of
the app (and of tdconv) will be system root ("/"), which is NOT writable, at
least on MacOS. When the app is invoked from the terminal via "open", or
app.py is run with  "python app.py", the working directory is the shell's
current directory.

"""

from __future__ import print_function
from __future__ import unicode_literals

from argparse import Namespace
import logging
import os
import queue

import tkFileDialog
from tkinter import (
    Tk,
    Button,
    Entry,
    Frame,
    Label,
    LabelFrame,
    StringVar,
    Radiobutton,
    Checkbutton,
    IntVar,
    N, NW, NE, S, E, W,
    X, LEFT, RIGHT, BOTH, SUNKEN, END,
)
from tkinter.scrolledtext import ScrolledText
import ttk
import traceback

from tdconv.tdconv import convert

logger = logging.getLogger("tdconv")


OPML = 'opml'
ZIP = 'zip'
CSV = 'csv'


class App:

    FMT_TASKPAPER = ("TaskPaper", "taskpaper")
    FMT_OPML = ("OPML", "opml")
    FMT_MD = ("Markdown", "md")
    FMT_CSV = ("Todoist (CSV)", "todoist")

    FROM_CSV = (FMT_TASKPAPER, FMT_OPML, FMT_MD)
    FROM_OPML = (FMT_CSV,)
    FROM_ZIP = (FMT_TASKPAPER, FMT_OPML, FMT_MD)

    def __init__(self, master):

        self.source_type = None
        self.build_gui(master)

    def build_gui(self, master):
        master.title("todoist converter v0.4")

        # source file
        self.filename = StringVar()
        self.filename.trace("w", lambda name, index, mode, source=self.filename: self.cb_source_file_changed(source))

        source_frame = Frame(master)
        source_frame.pack(anchor=NW, padx=10, pady=10)
        Label(source_frame, text="File to convert (CSV or OPML):").pack(side=LEFT)
        Entry(source_frame, text="foobar", textvariable=self.filename).pack(side=LEFT)
        Button(source_frame, text="Select File", command=self.cb_select_file).pack(side=LEFT)

        # separator
        # Frame(height=2, bd=1, relief=SUNKEN).pack(fill=X, padx=5, pady=5)

        # notebook = ttk.Notebook(master)
        # file_frame = ttk.Frame(notebook)
        # directory_frame = ttk.Frame(notebook)
        # notebook.add(file_frame, text='Process File')
        # notebook.add(directory_frame, text='Process Directory')

        # file format
        self.format = StringVar()
        self.format_frame = Frame(master)
        self.format_frame.pack(anchor=NW, padx=10, pady=10)
        self.make_format_frame(self.FMT_TASKPAPER[1], self.FROM_CSV)

        # download attachments
        self.download = IntVar()
        download_frame = Frame(master)
        download_frame.pack(anchor=NW)
        self.checkbox_download = Checkbutton(download_frame, text="Download Attachments?", variable=self.download)
        self.checkbox_download.pack(side=LEFT, padx=10, pady=10)

        # output file
        self.output_file = StringVar()
        output_frame = Frame(master)
        output_frame.pack(anchor=NW, padx=10, pady=10)
        Label(output_frame, text="Output file (derived from input if empty):").pack(side=LEFT)
        self.entry_target_file = Entry(output_frame, text="foobar", textvariable=self.output_file)
        self.entry_target_file.pack(side=LEFT, padx=10, pady=10)

        # buttons: convert, quit
        buttons_frame = Frame(master)
        buttons_frame.pack(anchor=NW, fill=X)
        self.button_convert = Button(buttons_frame, text="Convert", command=self.convert)
        self.button_convert.pack(anchor=NW, side=LEFT)

        logger_frame = LabelFrame(master, text="Converter Output:", padx=5, pady=5)
        logger_frame.pack(anchor=NW, fill=X, padx=10, pady=10)
        self.console = ConsoleUi(logger_frame, master)

    def make_format_frame(self, default, available_formats):
        """Set available output formats."""

        # destroy all widgets of frame
        for widget in self.format_frame.winfo_children():
            widget.destroy()

        self.format.set(default)
        Label(self.format_frame, text="Convert to: ").pack(side=LEFT)
        for text, mode in available_formats:
            self.select_format = Radiobutton(self.format_frame, text=text, variable=self.format, value=mode)
            self.select_format.pack(side=LEFT)

    def cb_source_file_changed(self, source):
        """Determine what kind of source file is selected."""

        name = source.get()

        if name.lower().endswith('csv'):
            self.source_type = CSV
            self.make_format_frame(self.FMT_TASKPAPER[1], self.FROM_CSV)
        elif name.lower().endswith('opml'):
            self.source_type = OPML
            self.make_format_frame(self.FMT_CSV[1], self.FROM_OPML)
        elif name.lower().endswith('zip'):
            self.source_type = ZIP
            self.make_format_frame(self.FMT_TASKPAPER[1], self.FROM_ZIP)
        else:
            self.source_type = None

    def cb_select_file(self):
        filename = tkFileDialog.askopenfilename(initialdir=".",
                                                title="Select file",
                                                defaultextension='*.csv',
                                                filetypes=(("Todoist Files", "*.csv"),
                                                           ("OPML Files", "*.opml"),
                                                           ("all files", "*.*")))
        print(filename)
        self.filename.set(filename)

    def convert(self):
        source = self.filename.get()
        if not source:
            logger.error("No source file set!!")
            return
        elif not os.path.exists(source):
            logger.error("source '%s' does not exist!" % source)
            return
        logger.setLevel('INFO')
        logger.info("starting conversion...")
        logger.info("source: %s" % source)
        logger.info("target: %s" % self.output_file.get())
        logger.info("format: %s" % self.format.get())
        logger.info("download attachments: %s" % self.download.get())
        logger.info("output folder: %s" % os.getcwd())

        args = Namespace(file=source,
                         format=self.format.get(),
                         output=self.output_file.get(),
                         download=self.download.get())
        try:
            convert(args)
        except Exception:
            tb = traceback.format_exc()
            logger.error(tb)
        else:
            logger.info("conversion finished")
        logger.info("ready")


class TargetDirectoryDoesNotExistError(Exception):
    pass


def make_target_filename(source, output, ext):
    """Return target filename:
        - for source != zip or directory: target file is source file with new extension
        - if output starts with os.sep, it's is considered full path
        - otherwise output  is considered a filename root
    """
    def _make_target_directory(source_dir, output):
        if output:
            if output.startswith(os.sep):
                target = output
            else:
                target = os.path.join(source_dir, output)
            if not os.path.isdir(target):
                raise TargetDirectoryDoesNotExistError("Output dir '%s' does not exist" % target)
            return target
        return source_dir

    if os.path.isdir(source):
        # source is a directory --> target needs to be a directory, too
        return _make_target_directory(source, output)
    else:
        # source is a file
        root, source_ext = os.path.splitext(source)
        head, tail = os.path.split(source)
        if source_ext.lower() == '.zip':
            # source is a zipfile --> target needs to be a directory
            return _make_target_directory(head, output)
        else:
            # source is a single file --> target is a file, too
            if output.startswith(os.sep):
                return output
            elif output:
                new_root = output
            else:
                new_root = tail
            new_name = '.'.join((os.path.splitext(new_root)[0], ext))
            return os.path.join(head, new_name)


class QueueHandler(logging.Handler):
    """Class to send logging records to a queue

    It can be used from different threads
    """
    def __init__(self, log_queue):
        super(QueueHandler, self).__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)


class ConsoleUi:
    """Poll messages from a logging queue and display them in a scrolled text widget"""

    def __init__(self, frame, master):
        self.frame = frame
        # Create a ScrolledText wdiget
        self.scrolled_text = ScrolledText(frame, state='disabled', height=12)
        self.scrolled_text.grid(row=0, column=0, sticky=(N, S, W, E))
        self.scrolled_text.configure(font='TkFixedFont')
        self.scrolled_text.tag_config('INFO', foreground='black')
        self.scrolled_text.tag_config('DEBUG', foreground='gray')
        self.scrolled_text.tag_config('WARNING', foreground='orange')
        self.scrolled_text.tag_config('ERROR', foreground='red')
        self.scrolled_text.tag_config('CRITICAL', foreground='red', underline=1)
        # Create a logging handler using a queue
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(message)s')
        self.queue_handler.setFormatter(formatter)
        logger.addHandler(self.queue_handler)
        # Start polling messages from the queue
        self.frame.after(100, self.poll_log_queue)
        self.scrolled_text.pack(fill=BOTH, expand=1)
        self.button_quit = Button(self.frame, text="Quit", fg="red", command=master.quit)
        self.button_quit.pack(anchor=NE, side=RIGHT)

    def display(self, record):
        msg = self.queue_handler.format(record)
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(END, msg + '\n', record.levelname)
        self.scrolled_text.configure(state='disabled')
        # Autoscroll to the bottom
        self.scrolled_text.yview(END)

    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display
        while True:
            try:
                record = self.log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.display(record)
        self.frame.after(100, self.poll_log_queue)


def main():
    root = Tk()
    App(root)
    os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "python" to true' ''')
    root.mainloop()
    root.destroy()


if __name__ == "__main__":
    main()
