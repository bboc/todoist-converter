# -*- coding: utf-8 -*-

from argparse import Namespace
import filecmp
import os
import shutil
import tempfile
import unittest

from tdconv.tdconv import convert

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

    def compare_files(self, a, b):
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
        args = Namespace(file=self.file, format='md', download=False, output=None)
        self._run_test_and_compare_results(args, 'basic-test.md', 'basic-test--result.md')

    def test_basic_conversion_to_opml(self):
        args = Namespace(file=self.file, format='opml', output=None)
        self._run_test_and_compare_results(args,  'basic-test.opml', 'basic-test--result.opml')


class UnicodeConverterTests(TodoistConverterTests):
    def test_basic_conversion_to_csv(self):
        args = Namespace(file=make_path('basic-opml-test.opml'), format='todoist', output=None)
        self._run_test_and_compare_results(args, 'basic-opml-test.csv', 'basic-opml-test--result.csv')

    def test_unicode_conversion_to_md(self):
        args = Namespace(file=make_path('unicode-and-quotes.csv'), format='md', download=True, output=None)
        self._run_test_and_compare_results(args, 'unicode-and-quotes.md', 'unicode-and-quotes--result.md')
    
    def test_unicode_conversion_to_opml(self):
        args = Namespace(file=make_path('unicode-and-quotes.csv'), format='opml', output=None)
        self._run_test_and_compare_results(args, 'unicode-and-quotes.opml', 'unicode-and-quotes--result.opml')

    def test_unicode_conversion_to_csv(self):
        args = Namespace(file=make_path('unicode-opml.opml'), format='todoist', output=None)
        self._run_test_and_compare_results(args,'unicode-opml.csv',
                                           'unicode-opml--result.csv')


class FullProjectConverterTests(TodoistConverterTests):
    def setUp(self):
        self.file = make_path('full-todoist-project.csv')
        super(FullProjectConverterTests, self).setUp()

    def test_conversion_to_md_with_download(self):
        args = Namespace(file=self.file, format='md', download=True, output=None)
        self._run_test_and_compare_results(args, 'full-todoist-project.md',
                                                 'full-todoist-project--result-download.md')

    def test_conversion_to_md(self):
        args = Namespace(file=self.file, format='md', download=False, output=None)
        self._run_test_and_compare_results(args,'full-todoist-project.md',
                                                'full-todoist-project--result.md')

    def test_todoist_to_taskpaper(self):
        args = Namespace(file=self.file, format='taskpaper', download=False, output=None)
        self._run_test_and_compare_results(args,'full-todoist-project.taskpaper',
                                                'full-todoist-project--result.taskpaper')
    
    def test_todoist_to_taskpaper_with_download(self):
        args = Namespace(file=self.file, format='taskpaper', download=True, output=None)
        self._run_test_and_compare_results(args, 'full-todoist-project.taskpaper',
                                                 'full-todoist-project--result-download.taskpaper')


class OuptutFileTests(TodoistConverterTests):
    def setUp(self):
        self.file = make_path('basic-test.csv')
        super(OuptutFileTests, self).setUp()

    def _test_output_file(self, format, output, result):
        args = Namespace(file=self.file, format=format, download=False, output=output)
        self._run_test_and_compare_results(args, output, result)


    def test_output_file_for_md(self):
        self._test_output_file('md', 'my-special-name.md', 'basic-test--result.md')

    def test_output_file_for_taskpaper(self):
        self._test_output_file('taskpaper', 'my-special-name.taskpaper', 'basic-test--result.taskpaper')

    def test_output_file_for_opml(self):
        self._test_output_file('opml', 'my-special-name.opml', 'basic-test--result.opml')

    def test_output_file_for_todoist(self):
        output = 'foobar.csv'
        args = Namespace(file=make_path('basic-opml-test.opml'), format='todoist', download=False, output=output)
        self._run_test_and_compare_results(args, output, 'basic-opml-test--result.csv')

    def _test_appending_output(self, output, format, result):
        args = Namespace(file=self.file, format=format, download=False, output=output)
        convert(args)
        args = Namespace(file=self.file, format=format, download=False, output=output)
        convert(args)
        self._compare_results(os.path.join(self.results, output),
                             make_path(result))

    def test_output_of_two_files_to_md(self):
        self._test_appending_output('combined-output.md', 'md', 'basic-test--result-combined.md')

    def test_output_of_two_files_to_taskpaper(self):
        self._test_appending_output('combined-output.taskpaper', 'taskpaper', 'basic-test--result-combined.taskpaper')


