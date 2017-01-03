# -*- coding: utf-8 -*-

import filecmp
from tdconv.tdconv import convert
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
    """Base class for file-based converter tests."""
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

    def _compare_results(self, result_file, correct_file):
        """Compare the actual result with the correct result."""
        with file(correct_file, 'r+') as correct:
            c = correct.readlines()
            with file(result_file, 'r+') as result:
                r = result.readlines()
                self.assertEqual(c, r)

    def compare_files(self, a,b):
        self.assertTrue(filecmp.cmp(a, b, shallow=False))

    def _run_test_and_compare_results(self, args, output_name, result_file_name):
        convert(args)
        self._compare_results(os.path.join(self.results, output_name),
                             make_path(result_file_name))


class BasicConverterTests(TodoistConverterTests):
    def setUp(self):
        self.file = make_path('basic-test.csv')
        super(BasicConverterTests, self).setUp()

    def test_basic_conversion_to_md(self):
        args = Namespace(file=self.file, format='md', download=False)
        self._run_test_and_compare_results(args, 'basic-test.md', 'basic-test--result.md')

    def test_basic_conversion_to_opml(self):
        args = Namespace(file=self.file, format='opml')
        self._run_test_and_compare_results(args,  'basic-test.opml', 'basic-test--result.opml')


class UnicodeConverterTests(TodoistConverterTests):
    def test_basic_conversion_to_csv(self):
        args = Namespace(file=make_path('basic-opml-test.opml'), format='todoist')
        self._run_test_and_compare_results(args, 'basic-opml-test.csv', 'basic-opml-test--result.csv')

    def test_unicode_conversion_to_md(self):
        args = Namespace(file=make_path('unicode-and-quotes.csv'), format='md', download=True)
        self._run_test_and_compare_results(args, 'unicode-and-quotes.md', 'unicode-and-quotes--result.md')
    
    def test_unicode_conversion_to_opml(self):
        args = Namespace(file=make_path('unicode-and-quotes.csv'), format='opml')
        self._run_test_and_compare_results(args, 'unicode-and-quotes.opml', 'unicode-and-quotes--result.opml')

    def test_unicode_conversion_to_csv(self):
        args = Namespace(file=make_path('unicode-opml.opml'), format='todoist')
        self._run_test_and_compare_results(args,'unicode-opml.csv',
                                           'unicode-opml--result.csv')


class FullProjectConverterTests(TodoistConverterTests):
    def setUp(self):
        self.file = make_path('full-todoist-project.csv')
        super(FullProjectConverterTests, self).setUp()

    def test_conversion_to_md_with_download(self):
        args = Namespace(file=self.file, format='md', download=True)
        self._run_test_and_compare_results(args, 'full-todoist-project.md',
                                                 'full-todoist-project--result-download.md')

    def test_conversion_to_md(self):
        args = Namespace(file=self.file, format='md', download=False)
        self._run_test_and_compare_results(args,'full-todoist-project.md',
                                                'full-todoist-project--result.md')

    def test_todoist_to_taskpaper(self):
        args = Namespace(file=self.file, format='taskpaper', download=False)
        self._run_test_and_compare_results(args,'full-todoist-project.taskpaper',
                                                'full-todoist-project--result.taskpaper')
    
    def test_todoist_to_taskpaper_with_download(self):
        args = Namespace(file=self.file, format='taskpaper', download=True)
        self._run_test_and_compare_results(args, 'full-todoist-project.taskpaper',
                                                 'full-todoist-project--result-download.taskpaper')
