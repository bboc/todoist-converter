# -*- coding: utf-8 -*-

import os
import shutil
import unittest

from app import make_target_filename


# class TargetFilenameForDirectoryTests(unittest.TestCase):
#     """Test deriving target filename for app."""

#     def test_no_output(self):
#         """Target should be the same as source."""
#         self.fail()

#     def test_no_pathsep(self):
#         """Output without os.sep should be considered existing subfolder of source."""
#         self.fail()

#     def test_pathsep(self):
#         """Output with a pathsep should be treated as existing folder."""
#         self.fail()


# class TargetFilenameForZipTests(unittest.TestCase):
#     """Test deriving target filename for a zip file."""

#     def test_no_output(self):
#         """Target should be the directory the source is located in."""
#         self.fail()

#     def test_no_pathsep(self):
#         """Output without os.sep should be considered existing subfolder of source."""
#         self.fail()

#     def test_pathsep(self):
#         """Output with a pathsep should be treated as existing folder."""
#         self.fail()


class TargetFilenameForFilesTests(unittest.TestCase):
    """Test deriving target filename for a zip file."""

    def test_no_output(self):
        """Target should source file with a new extension."""
        t = make_target_filename("/Users/foobar/test/mystuff.csv", "", "taskpaper")
        self.failUnlessEqual(t, "/Users/foobar/test/mystuff.taskpaper")

    def test_simple_output(self):
        """Output without os.sep in the beginning should be file in same directory than source."""
        t = make_target_filename("/Users/foobar/test/mystuff.csv", "result", "taskpaper")
        self.failUnlessEqual(t, "/Users/foobar/test/result.taskpaper")

        t = make_target_filename("/Users/foobar/test/mystuff.csv", "result/file", "taskpaper")
        self.failUnlessEqual(t, "/Users/foobar/test/result/file.taskpaper")

    def test_output_with_pathsep(self):
        """Output with a os.sep in beginningis a complete new filename."""
        t = make_target_filename("/Users/foobar/test/mystuff.csv", "/result/file.ext", "taskpaper")
        self.failUnlessEqual(t, "/result/file.ext")
