# -*- coding: utf-8 -*-

import filecmp
from tdconv import convert
import os
import shutil
import sys
import tempfile
import unittest
from argparse import Namespace


def data_dir():
    """Directory of test files."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                        'test-data')    

def make_path(*args):
    return os.path.join(data_dir(), *args)


class TodoistConverterTests(unittest.TestCase):

    def setUp(self):
        """
        Create temp folder and point working directory there, 
        clean up temp folder and working directory afterwards.
        """
        self.maxDiff = None
        self.results = tempfile.mkdtemp()
        self.test_data = data_dir()
        cwd = os.getcwd()
        os.chdir(self.results)
        self.addCleanup(shutil.rmtree, self.results)
        self.addCleanup(os.chdir, cwd)

    def compare_results(self, result_file, correct_file):
        """Compare the actual result with the correct result."""
        with file(correct_file, 'r+') as correct:
            c = correct.readlines()
            with file(result_file, 'r+') as result:
                r = result.readlines()
                self.assertEqual(c, r)

    def compare_files(self, a,b):
        self.assertTrue(filecmp.cmp(a, b, shallow=False))


    def test_basic_conversion_to_md(self):
        args = Namespace(file=make_path('basic-test.csv'), format='md')
        convert(args)
        self.compare_results(os.path.join(self.results, 'basic-test.md'),
                             make_path('basic-test.md'))

    def test_basic_conversion_to_opml(self):
        args = Namespace(file=make_path('basic-test.csv'), format='opml')
        convert(args)
        self.compare_results(os.path.join(self.results, 'basic-test.opml'),
                             make_path('basic-test.opml'))

    def test_basic_conversion_to_csv(self):
        args = Namespace(file=make_path('opml-test.opml'), format='todoist')
        convert(args)
        self.compare_results(os.path.join(self.results, 'opml-test.csv'),
                             make_path('opml-test-roundtrip.csv'))


    def test_unicode_conversion_to_md(self):
        args = Namespace(file=make_path('test-unicode-and-quotes.csv'), format='md')
        convert(args)
        self.compare_results(os.path.join(self.results, 'test-unicode-and-quotes.md'),
                             make_path('test-unicode-and-quotes.md'))
    
    def test_unicode_conversion_to_opml(self):
        args = Namespace(file=make_path('test-unicode-and-quotes.csv'), format='opml')
        convert(args)
        self.compare_results(os.path.join(self.results, 'test-unicode-and-quotes.opml'),
                             make_path('test-unicode-and-quotes.opml'))

    def test_unicode_conversion_to_csv(self):
        args = Namespace(file=make_path('opml-unicode-test.opml'), format='todoist')
        convert(args)
        self.compare_results(os.path.join(self.results, 'opml-unicode-test.csv'),
                             make_path('opml-unicode-result.csv'))
