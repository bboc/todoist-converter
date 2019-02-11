# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

from argparse import Namespace
import os

from Tkinter import *
import tkFileDialog

from tdconv.tdconv import convert


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
        convert(args)


def main():
    root = Tk()
    app = App(root)
    os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "python" to true' ''')
    root.mainloop()
    root.destroy()


if __name__ == "__main__":
    main()
