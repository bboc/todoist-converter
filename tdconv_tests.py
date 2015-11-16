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
                             make_path('basic-result.md'))

    def test_basic_conversion_to_opml(self):
        args = Namespace(file=make_path('basic-test.csv'), format='opml')
        convert(args)
        self.compare_results(os.path.join(self.results, 'basic-test.opml'),
                             make_path('basic-result.opml'))

    def test_basic_conversion_to_csv(self):
        args = Namespace(file=make_path('basic-opml-test.opml'), format='todoist')
        convert(args)
        self.compare_results(os.path.join(self.results, 'basic-opml-test.csv'),
                             make_path('basic-opml-result.csv'))


    def test_unicode_conversion_to_md(self):
        args = Namespace(file=make_path('unicode-and-quotes-test.csv'), format='md')
        convert(args)
        self.compare_results(os.path.join(self.results, 'unicode-and-quotes-test.md'),
                             make_path('unicode-and-quotes-result.md'))
    
    def test_unicode_conversion_to_opml(self):
        args = Namespace(file=make_path('unicode-and-quotes-test.csv'), format='opml')
        convert(args)
        self.compare_results(os.path.join(self.results, 'unicode-and-quotes-test.opml'),
                             make_path('unicode-and-quotes-result.opml'))

    def test_unicode_conversion_to_csv(self):
        args = Namespace(file=make_path('unicode-opml-test.opml'), format='todoist')
        convert(args)
        self.compare_results(os.path.join(self.results, 'unicode-opml-test.csv'),
                             make_path('unicode-opml-result.csv'))
