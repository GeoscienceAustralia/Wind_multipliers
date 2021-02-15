"""
Perform a PEP8 conformance test of the wind multiplier code base.

"""
from os.path import dirname, abspath, exists, join as pjoin
import unittest
import pep8


class TestCodeFormat(unittest.TestCase):
    def test_pep8_conformance(self):
        # Tests the wind multiplier code base against the "pep8" tool.
        #
        # Users can add their own excluded files (should files exist in the
        # local directory which is not in the repository) by adding a
        # ".pep8_test_exclude.txt" file in the same directory as this test.
        # The file should be a line separated list of filenames/directories
        # as can be passed to the "pep8" tool's exclude list.

        pep8style = pep8.StyleGuide(quiet=False)
        pep8style.options.exclude.extend(['*/_version.py'])

        # Allow users to add their own exclude list.
        extra_exclude_file = pjoin(dirname(__file__), '.pep8_test_exclude.txt')
        if exists(extra_exclude_file):
            with open(extra_exclude_file, 'r') as fhandle:
                extra_exclude = [line.strip()
                                 for line in fhandle if line.strip()]
            pep8style.options.exclude.extend(extra_exclude)

        root = dirname(dirname(abspath(__file__)))
        result = pep8style.check_files([root])
        self.assertEqual(result.total_errors, 0,
                         "Found code syntax errors (and warnings).")


if __name__ == '__main__':
    unittest.main()
