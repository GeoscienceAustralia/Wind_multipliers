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
import sys
import unittest

import numpy as np

from parallel import attempt_parallel


class TestParallel(unittest.TestCase):

    def setUp(self):
        cmd_folder = os.path.dirname(os.path.realpath(__file__))

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

    def test_commworld_creation(self):
        global comm
        assert comm.name == 'DummyCommWorld' or comm.name == 'MPI_COMM_WORLD'
        assert comm.size == 1
        assert comm.rank == 0
        assert comm.Get_size() == 1
        assert comm.Get_rank() == 0

    def test_commworld_scatter_gather(self):
        if comm.rank == 0:
            tiles = [np.array([1, 2, 3])]
        else:
            tiles = None
        local_tiles = comm.scatter(tiles, root=0)
        np.testing.assert_almost_equal(local_tiles, np.array([1, 2, 3]), decimal=2,
                                       err_msg='', verbose=True)
        # assert local_tiles == tiles[0]
        local_results = local_tiles * 2
        results = comm.gather(local_results, root=0)
        np.testing.assert_almost_equal(results[0], np.array([2, 4, 6]), decimal=2,
                                       err_msg='', verbose=True)


if __name__ == "__main__":
    unittest.main()
