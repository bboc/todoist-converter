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
import glob

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
    X, LEFT, RIGHT, BOTH, END,
)
from tkinter.scrolledtext import ScrolledText
import traceback
import ttk

from tdconv.tdconv import convert, determine_target_directory

from setup import VERSION

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

    DIR_SOURCE_FORMATS = (FMT_CSV, FMT_OPML)

    FILES_CONVERSION_TAB = 0
    DIRECTORY_CONVERSION_TAB = 1

    TARGET_FORMAT_FRAME_LABEL = "Convert to:"

    def __init__(self, master):

        self.source_type = None
        self.build_gui(master)

    def build_gui(self, master):
        master.title("todoist converter v%s" % VERSION)

        # separator
        # Frame(height=2, bd=1, relief=SUNKEN).pack(fill=X, padx=5, pady=5)

        self.notebook = ttk.Notebook(master)
        file_frame = Frame(self.notebook)
        directory_frame = Frame(self.notebook)
        self.notebook.add(file_frame, text='Process File')
        self.notebook.add(directory_frame, text='Process Directory')
        self.notebook.pack(anchor=NW, padx=10, pady=10)
        self.style_notebook()

        self.make_file_frame(file_frame)
        self.make_directory_frame(directory_frame)

        # buttons: convert
        buttons_frame = Frame(master)
        buttons_frame.pack(anchor=NW, fill=X)
        self.button_convert = Button(buttons_frame, text="Convert", command=self.convert)
        self.button_convert.pack(anchor=NW, side=LEFT)

        logger_frame = LabelFrame(master, text="Converter Output:", padx=5, pady=5)
        logger_frame.pack(anchor=NW, fill=X, padx=10, pady=10)
        self.console = ConsoleUi(logger_frame, master)

    def style_notebook(self):
        grey = "#d2d2d2"
        white = "#ffffff"

        style = ttk.Style()

        style.theme_create("blueish", parent="alt", settings={
            "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0]}},
            "TNotebook.Tab": {
                "configure": {"padding": [5, 5], "background": grey},
                "map": {"background": [("selected", white)],
                        "expand": [("selected", [1, 1, 1, 0])]}}})
        style.theme_use("blueish")

    def make_file_frame(self, frame):
        # source file
        self.filename = StringVar()
        self.filename.trace("w", lambda name, index, mode, source=self.filename: self.cb_source_file_changed(source))

        source_frame = Frame(frame)
        source_frame.pack(anchor=NW, padx=10, pady=10)
        Label(source_frame, text="File to convert (CSV or OPML):").pack(side=LEFT)
        Entry(source_frame, text="foobar", textvariable=self.filename).pack(side=LEFT)
        Button(source_frame, text="Select File", command=self.cb_select_file).pack(side=LEFT)

        # file format
        self.format = StringVar()
        self.format_frame = Frame(frame)
        self.format_frame.pack(anchor=NW, padx=10, pady=10)
        self._make_format_frame(self.format_frame, self.TARGET_FORMAT_FRAME_LABEL, self.format, self.FMT_TASKPAPER[1], self.FROM_CSV)

        # download attachments
        self.download = IntVar()
        download_frame = Frame(frame)
        download_frame.pack(anchor=NW)
        self.checkbox_download = Checkbutton(download_frame, text="Download Attachments?", variable=self.download)
        self.checkbox_download.pack(side=LEFT, padx=10, pady=10)

        # output file
        self.output_file = StringVar()
        output_frame = Frame(frame)
        output_frame.pack(anchor=NW, padx=10, pady=10)
        Label(output_frame, text="Output file (derived from input if empty):").pack(side=LEFT)
        self.entry_target_file = Entry(output_frame, text="foobar", textvariable=self.output_file)
        self.entry_target_file.pack(side=LEFT, padx=10, pady=10)

    def make_directory_frame(self, frame):
        # source file
        self.dirname = StringVar()

        source_frame = Frame(frame)
        source_frame.pack(anchor=NW, padx=10, pady=10)
        Label(source_frame, text="Select a directory:").pack(side=LEFT)
        Entry(source_frame, text="", textvariable=self.dirname).pack(side=LEFT)
        Button(source_frame, text="Select Directory", command=self.cb_select_dir).pack(side=LEFT)

        # source format
        self.dir_source_format = StringVar()

        source_format_frame = Frame(frame)
        source_format_frame.pack(anchor=NW, padx=10, pady=10)
        self._make_format_frame(source_format_frame, "Source format:", self.dir_source_format, 'todoist', self.DIR_SOURCE_FORMATS)
        self.dir_source_format.trace("w", lambda name, index, mode, source_format=self.dir_source_format: self.cb_dir_source_format_changed(source_format))

        # init all variables for options before populating the frame
        self.dir_target_format = StringVar()
        self.dir_download_attachments = IntVar()
        self.dir_collect_to_one_file = IntVar()  # TODO: entry and processing still missing

        self.dir_options_frame = LabelFrame(frame, text="Format Options:", padx=5, pady=5)
        self.dir_options_frame.pack(anchor=NW, fill=X, padx=10, pady=10)

        self.make_dir_csv_options_frame(self.dir_options_frame)

    def make_dir_csv_options_frame(self, frame):

        self.clean_frame(frame)
        # file format
        format_frame = Frame(frame)
        format_frame.pack(anchor=NW, padx=10, pady=10)
        self._make_format_frame(format_frame, self.TARGET_FORMAT_FRAME_LABEL, self.dir_target_format, self.FMT_TASKPAPER[1], self.FROM_CSV)

        # download attachments
        download_frame = Frame(frame)
        download_frame.pack(anchor=NW)
        checkbox_download = Checkbutton(download_frame, text="Download Attachments?", variable=self.dir_download_attachments)
        checkbox_download.pack(side=LEFT, padx=10, pady=10)

    def _make_format_frame(self, frame, label, variable, default, available_formats):
        """Set available output formats."""
        variable.set(default)
        Label(frame, text=label).pack(side=LEFT)
        for text, mode in available_formats:
            Radiobutton(frame, text=text, variable=variable, value=mode).pack(side=LEFT)

    def clean_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def cb_source_file_changed(self, source):
        """Determine what kind of source file is selected."""

        name = source.get()
        logger.debug(name)

        def switch_format(source_type, default, available_formats):
            self.source_type = source_type
            self.clean_frame(self.format_frame)
            self._make_format_frame(self.format_frame, self.TARGET_FORMAT_FRAME_LABEL, self.format, default, available_formats)

        if name.lower().endswith('csv'):
            switch_format(CSV, self.FMT_TASKPAPER[1], self.FROM_CSV)
        elif name.lower().endswith('opml'):
            switch_format(OPML, self.FMT_CSV[1], self.FROM_OPML)
        elif name.lower().endswith('zip'):
            switch_format(ZIP, self.FMT_TASKPAPER[1], self.FROM_ZIP)
        else:
            self.source_type = None

    def cb_dir_source_format_changed(self, source_format):

        format = source_format.get()
        if format == self.FMT_OPML[1]:
            self.clean_frame(self.dir_options_frame)
        elif format == self.FMT_CSV[1]:
            self.make_dir_csv_options_frame(self.dir_options_frame)
        else:
            raise Exception("unknown source format %s" % format)

    def cb_select_file(self):
        filename = tkFileDialog.askopenfilename(initialdir=".",
                                                title="Select file",
                                                defaultextension='*.csv',
                                                filetypes=(("Todoist Files", "*.csv"),
                                                           ("OPML Files", "*.opml"),
                                                           ("ZIP Files", "*.zip"),
                                                           ("all files", "*.*")))
        self.filename.set(filename)

    def cb_select_dir(self):
        dirname = tkFileDialog.askdirectory()
        self.dirname.set(dirname)

    def convert(self):
        """Trigger conversion of source(s) to desired target format."""
        logger.setLevel('INFO')
        # logger.setLevel('DEBUG')
        logger.info("starting conversion...")

        nb_idx = self.notebook.index(self.notebook.select())

        if nb_idx == self.FILES_CONVERSION_TAB:
            # set parameters for file conversion
            logger.debug("files tab")
            source = self.filename.get()
            target_format = self.format.get()
            logger.debug("target format: %s" % target_format)
            output = make_target_filename(source, self.output_file.get(), target_format)
            download_attachments = self.download.get()
            self.tdconv(source, target_format, output, download_attachments)
        elif nb_idx == self.DIRECTORY_CONVERSION_TAB:
            logger.debug("directory tab")
            source = self.dirname.get()
            source_filter = self.dir_source_format.get()
            target_format = self.dir_target_format.get()
            download_attachments = self.dir_download_attachments.get()
            self.process_directory(source, source_filter, target_format, download_attachments)
        else:
            raise Exception("unknown tab %s" % nb_idx)

        logger.info("ready")

    def process_directory(self, source, source_filter, target_format, download_attachments):
        """Process all files in a directory that match source_filter"""
        if not os.path.isdir(source):
            raise Exception("Source '%s' is not a directory" % source)

        ext = source_filter
        if source_filter == 'todoist':
            ext = 'csv'
        pattern = '*.%s' % ext
        source_files = glob.glob(os.path.join(source, pattern))

        if source_files:
            for s in source_files:
                o = make_target_filename(s, '', target_format)
                self.tdconv(s, target_format, o, download_attachments)
        else:
            logger.error("No files matching pattern '%s' in directory '%s'" % (pattern, source))

    def tdconv(self, source, target_format, output, download_attachments):
        """Call tdconv to convert a file."""
        # make sure source exists
        if not source:
            logger.error("No source file set!!")
            return
        elif not os.path.exists(source):
            logger.error("source '%s' does not exist!" % source)
            return
        logger.info("source: %s" % source)
        logger.info("target: %s" % output)
        logger.info("format: %s" % target_format)
        logger.info("download attachments: %s" % download_attachments)

        args = Namespace(file=source,
                         format=target_format,
                         output=output,
                         download=download_attachments)
        try:
            pass
            convert(args)
        except Exception:
            tb = traceback.format_exc()
            logger.error(tb)
        else:
            logger.info("conversion finished")


def make_target_filename(source, output, ext):
    """Return target filename:
        - for source != zip or directory: target file is source file with new extension
        - if output starts with os.sep, it's is considered full path
        - otherwise output  is considered a filename root
    """
    if ext == 'todoist':
        ext = 'csv'

    if os.path.isdir(source):
        # source is a directory --> target needs to be a directory, too
        return determine_target_directory(source, output)
    else:
        # source is a file
        root, source_ext = os.path.splitext(source)
        head, tail = os.path.split(source)
        if source_ext.lower() == '.zip':
            # source is a zipfile --> target needs to be a directory
            return determine_target_directory(head, output)
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
