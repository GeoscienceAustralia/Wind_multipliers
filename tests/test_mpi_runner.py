"""
    Title: test_parallel.py
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

from utilities.convert import create_sub_dirs_for_convert
from utilities.mpi_runner import parallelise_convert_on_tiles
from utilities.parallel import attempt_parallel


class TestMPIRunner(unittest.TestCase):

    def setUp(self):
        cmd_folder = os.path.dirname(os.path.realpath(__file__))
        self.testdata_folder = os.path.join(cmd_folder, 'test_data')
        self.test_title = 'e113.5465s24.6626'

        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))
        if parent not in sys.path:
            sys.path.insert(0, parent)
        utilities = os.path.join(parent, 'utilities')
        if utilities not in sys.path:
            sys.path.insert(0, utilities)

        global MPI, comm
        MPI = attempt_parallel()
        import atexit
        atexit.register(MPI.Finalize)
        comm = MPI.COMM_WORLD

    def test_parallelise_convert_on_tiles(self):
        global comm
        data_path = os.path.join(self.testdata_folder, 'convert_data')
        output_path_m3 = os.path.join(data_path, 'M3')
        output_path_m3_max = os.path.join(data_path, 'M3_max')

        # Remove old files if exists
        if os.path.exists(output_path_m3):
            shutil.rmtree(output_path_m3)
        if os.path.exists(output_path_m3_max):
            shutil.rmtree(output_path_m3_max)

        create_sub_dirs_for_convert(data_path)
        parallelise_convert_on_tiles(data_path, comm)

        assert os.path.exists(os.path.join(output_path_m3,
                                           self.test_title + '.tif'))
        assert os.path.exists(os.path.join(output_path_m3,
                                           'wind-multipliers.vrt'))
        assert os.path.exists(os.path.join(output_path_m3_max,
                                           self.test_title + '.tif'))
        assert os.path.exists(os.path.join(output_path_m3_max,
                                           'wind-multipliers.vrt'))
        # self.assertIsNotNone(converter.tile_files)
        # for file in converter.tile_files:
        #     assert os.path.exists(file)
        #
        # self.assertIsNotNone(converter.max_tile_files)
        # for file in converter.max_tile_files:
        #     assert os.path.exists(file)


if __name__ == "__main__":
    unittest.main()
