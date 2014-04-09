#!/usr/bin/python2.6
import subprocess
import numpy as np
import read_output
import os
import unittest
from parametrized_test_case import ParametrizedTestCase
from misc import DIRECTIONS
from misc import TestPaths

"""
.. module:: test_topo
   :synopsis: Module used to initiate characterisation tests for topographic multiplier

.. moduleauthor:: Daniel Wild <daniel.wild@ga.gov.au>


"""




class TestOutput(ParametrizedTestCase):
    """Test Class used to run a unit test comparison of expected against actual results outputted by topomult.py

    """

    def test_TopoOutput(self):

        self.test_paths = TestPaths()
        self.test_paths.initTopoTestPaths(self.param)

        args = ['mpirun',
                '-mca', 'btl', '^openib',  # don't check for inifiniband
                '-np', '8',
                'python',  os.path.join(self.test_paths.TOPO_FILES_DIR, 'topomult.py'),
                '-i',  os.path.join(self.test_paths.TOPO_TEST_INPUT_DIR, 'dem.asc'),
                '-o',  self.test_paths.TOPO_TEST_ACTUAL_OUTPUT_DIR]

        subprocess.call(args)

        """Loops through each of the eight directions, reading input data into numpy array for comparison using
        np.allClose()

       """

        # need to loop through all directions..
        for aDirection in DIRECTIONS:

            print 'Dir:', aDirection

            expectedArray = read_output.read(os.path.join(self.test_paths.TOPO_TEST_EXPECTED_OUTPUT_DIR,
                                                        'mh_'+ aDirection + '_smooth.asc'))
            actualArray = read_output.read(os.path.join(self.test_paths.TOPO_TEST_ACTUAL_OUTPUT_DIR,
                                                        'mh_'+ aDirection + '_smooth.asc'))

            # ! allClose() will return False if NaN is detected
            result = np.allclose(expectedArray, actualArray)

            print "\n",aDirection, "test =", result

            self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()