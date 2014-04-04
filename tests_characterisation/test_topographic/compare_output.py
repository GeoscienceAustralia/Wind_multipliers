#!/usr/bin/python2.6
import unittest
import numpy as np
import read_output
import wind_directions

class TestOutput(unittest.TestCase):

    def test_TopoOutput(self):

        # need to loop through all directions..
        for aDirection in wind_directions.directions:

                print 'Dir:', aDirection

                expectedArray = read_output.read('test_topographic/topo_expected_output/mh_'+ aDirection +'.asc')
                actualArray = read_output.read('test_topographic/topo_actual_output/mh_'+ aDirection +'.asc')

                # ! allClose() will return False if NaN is detected
                result = np.allclose(expectedArray, actualArray)

                print "\n",aDirection, "test =", result


                self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()