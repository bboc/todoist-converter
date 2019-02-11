# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import os

import ttk
import Tkinter


class TestApp(object):

    def __init__(self, master):
            # separator
        ttk.Separator(master, orient=Tkinter.HORIZONTAL).pack()

        p = ttk.Panedwindow(master, orient=Tkinter.VERTICAL)
        p.pack()
        # first pane, which would get widgets gridded into it:
        f1 = ttk.Labelframe(p, text='Pane1', width=100, height=100)
        f2 = ttk.Labelframe(p, text='Pane2', width=100, height=100)   # second pane
        p.add(f1)
        p.add(f2)
        p.pack()


def main():
    root = Tkinter.Tk()
    app = TestApp(root)

    os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "python" to true' ''')
    root.mainloop()
    root.destroy()


if __name__ == "__main__":
    main()
