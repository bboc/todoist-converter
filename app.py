# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

from argparse import Namespace
import os

from tkinter import (
    Tk,
    Button,
    Entry,
    Frame,
    Label,
    StringVar,
    Radiobutton,
    Checkbutton,
    IntVar,
    N, NW, NE, S, E, W,
    X, LEFT, SUNKEN, END,
)
from tkinter.scrolledtext import ScrolledText
import tkFileDialog

from tdconv.tdconv import convert
import logging
import queue

logger = logging.getLogger("tdconv")


class App:

    AVAILABLE_FORMATS = [
        ("TaskPaper", "taskpaper"),
        ("OPML", "opml"),
        ("Markdown", "md"),
        ("Todoist (CSV)", "todoist"),
    ]

    def __init__(self, master):

        master.title("todoist-converter v0.3")

        # source file
        self.filename = StringVar()
        source_frame = Frame(master)
        source_frame.pack(anchor=NW)
        Label(source_frame, text="File to convert:").pack(side=LEFT)
        Entry(source_frame, text="foobar", textvariable=self.filename).pack(side=LEFT)
        Button(source_frame, text="Select File", command=self.cb_select_file).pack(side=LEFT)

        # separator
        Frame(height=2, bd=1, relief=SUNKEN).pack(fill=X, padx=5, pady=5)

        # output file
        self.output_file = StringVar()
        output_frame = Frame(master)
        output_frame.pack(anchor=NW)
        Label(output_frame, text="Output file (optional):").pack(side=LEFT)
        self.entry_target_file = Entry(output_frame, text="foobar", textvariable=self.output_file)
        self.entry_target_file.pack(side=LEFT)

        # separator
        Frame(height=2, bd=1, relief=SUNKEN).pack(fill=X, padx=5, pady=5)

        # file format
        self.format = StringVar()
        self.format.set("taskpaper")
        format_frame = Frame(master)
        format_frame.pack(anchor=NW)
        Label(format_frame, text="Convert to: ").pack(side=LEFT)
        for text, mode in self.AVAILABLE_FORMATS:
            self.select_format = Radiobutton(format_frame, text=text, variable=self.format, value=mode)
            self.select_format.pack(side=LEFT)

        # separator
        Frame(height=2, bd=1, relief=SUNKEN).pack(fill=X, padx=5, pady=5)

        # download attachments
        self.download = IntVar()
        download_frame = Frame(master)
        download_frame.pack(anchor=NW)
        self.checkbox_download = Checkbutton(download_frame, text="Download Attachments?", variable=self.download)
        self.checkbox_download.pack(side=LEFT)

        # separator
        Frame(height=2, bd=1, relief=SUNKEN).pack(fill=X, padx=5, pady=5)

        # buttons: convert, quit
        buttons_frame = Frame(master)
        buttons_frame.pack(anchor=NW, fill=X)
        self.button_quit = Button(buttons_frame, text="Quit", fg="red", command=master.quit)
        self.button_quit.pack(anchor=NW, side=LEFT)
        self.button_convert = Button(buttons_frame, text="Convert", command=self.convert)
        self.button_convert.pack(anchor=NE)

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
        # TODO: warn if filename not set
        print("format", self.format.get())
        print("download", self.download.get())
        print("source", self.filename.get())
        print("target", self.output_file.get())

        args = Namespace(file=self.filename.get(),
                         format=self.format.get(),
                         output=self.output_file.get(),
                         download=self.download.get())
        logger.warning("converting with %s" % repr(args))
        logger.debug(os.getcwd())
        convert(args)


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

    def __init__(self, frame):
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
        formatter = logging.Formatter('%(asctime)s: %(message)s')
        self.queue_handler.setFormatter(formatter)
        logger.addHandler(self.queue_handler)
        # Start polling messages from the queue
        self.frame.after(100, self.poll_log_queue)

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
