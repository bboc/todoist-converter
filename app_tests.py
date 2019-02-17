# -*- coding: utf-8 -*-

import os
import shutil
import unittest

from app import make_target_filename


class TargetFilenameForDirectoryTests(unittest.TestCase):
    """Test deriving target filename for app."""

    def test_no_output(self):
        """Target should be the same as source."""
        self.fail()

    def test_no_pathsep(self):
        """Output without os.sep should be considered existing subfolder of source."""
        self.fail()

    def test_pathsep(self):
        """Output with a pathsep should be treated as existing folder."""
        self.fail()


class TargetFilenameForZipTests(unittest.TestCase):
    """Test deriving target filename for a zip file."""

    def test_no_output(self):
        """Target should be the directory the source is located in."""
        self.fail()

    def test_no_pathsep(self):
        """Output without os.sep should be considered existing subfolder of source."""
        self.fail()

    def test_pathsep(self):
        """Output with a pathsep should be treated as existing folder."""
        self.fail()


class TargetFilenameForFilesTests(unittest.TestCase):
    """Test deriving target filename for a zip file."""

    def test_no_output(self):
        """Target should source file with a new extension."""
        make_target_filename("foo", "bar", "baz")
        self.fail()

    def test_no_pathsep(self):
        """Output without os.sep should be file in same directory than source."""
        self.fail()

    def test_pathsep(self):
        """Output with a pathsep should be treated as complete new filename."""
        self.fail()

