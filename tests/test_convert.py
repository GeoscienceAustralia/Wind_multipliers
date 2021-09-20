"""
    Title: test_convert.py
    Author: Mahmudul Hasan, mahmudul.hasan@ga.gov.au
    CreationDate: 2020-09-03
    Updated:
    Description: Unit testing module for Converter class in
                 convert.py
    Version: $Rev$
    $Id$
"""
import os.path
import shutil
import sys
import unittest

from utilities.convert import Converter, create_sub_dirs_for_convert
from convert import Converter, create_sub_dirs_for_convert


class TestConverter(unittest.TestCase):

    def setUp(self):
        cmd_folder = os.path.dirname(os.path.realpath(__file__))
        self.testdata_folder = os.path.join(cmd_folder, 'test_data')
        self.test_title = 'e113.5465s24.6626'

        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))
        if parent not in sys.path:
            sys.path.insert(0, parent)

    def test_run(self):
        data_path = os.path.join(self.testdata_folder, 'convert_data')
        output_path_m3 = os.path.join(data_path, 'M3')
        output_path_m3_max = os.path.join(data_path, 'M3_max')

        # Remove old files if exists
        if os.path.exists(output_path_m3):
            shutil.rmtree(output_path_m3)
        if os.path.exists(output_path_m3_max):
            shutil.rmtree(output_path_m3_max)

        create_sub_dirs_for_convert(data_path)
        converter = Converter([self.test_title], data_path)
        converter.run()

        self.assertIsNotNone(converter.tile_files)
        for file in converter.tile_files:
            assert os.path.exists(file)

        self.assertIsNotNone(converter.max_tile_files)
        for file in converter.max_tile_files:
            assert os.path.exists(file)


if __name__ == "__main__":
    unittest.main()
