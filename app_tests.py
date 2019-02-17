# -*- coding: utf-8 -*-

import os
import unittest

from app import make_target_filename, TargetDirectoryDoesNotExistError
from tdconv_tests import data_dir


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


class TargetFilenameForZipTests(unittest.TestCase):
    """Test deriving target filename for a zip file."""

    def test_no_output(self):
        """Target should be the directory the source is located in."""
        t = make_target_filename("/Users/foobar/test/mystuff.ZiP", "", "taskpaper")
        self.failUnlessEqual(t, "/Users/foobar/test")

    def test_simple_output(self):
        """Output without os.sep should be considered existing subfolder of source."""
        t = make_target_filename(os.path.join(data_dir(), "mystuff.ZiP"), "results", "taskpaper")
        self.failUnlessEqual(t, os.path.join(data_dir(), "results"))

    def test_simple_output_should_raise_exception(self):
        """Output without os.sep should raise an exception if target does not exist"""
        self.failUnlessRaises(TargetDirectoryDoesNotExistError,
                              make_target_filename, "/Users/foobar/test/mystuff.ZiP", "foo/bar", "taskpaper")

    def test_output_with_pathsep(self):
        """Output that starts with a os.sep is treated as complete path to existing folder."""
        t = make_target_filename("/Users/foobar/test/mystuff.ZiP", os.path.abspath(data_dir()), "taskpaper")
        self.failUnlessEqual(t, os.path.abspath(data_dir()))

    def test_output_with_pathsep_should_raise_exception(self):
        """Function should raise an exception if target does not exist"""
        """Output that starts with a os.sep is treated as complete path to existing folder."""
        self.failUnlessRaises(TargetDirectoryDoesNotExistError,
                              make_target_filename, "/Users/foobar/test/mystuff.ZiP", "/foo/bar", "taskpaper")


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
        """Output that starts with a os.sep is treated as complete path."""
        t = make_target_filename("/Users/foobar/test/mystuff.csv", "/result/file.ext", "taskpaper")
        self.failUnlessEqual(t, "/result/file.ext")