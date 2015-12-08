"""
    Title: testmultipliercalc.py
    Author: Tina Yang, tina.yang@ga.gov.au
    CreationDate: 2014-05-01
    Description: Unit testing module for multiplier_cal function in
                 multiplier_calc.py
    Version: $Rev$
    $Id$
"""

import sys
import os.path
import unittest
import numpy as np
from numpy.testing import assert_allclose
from matplotlib import pyplot
from inspect import getfile, currentframe

# import topographic.multiplier_calc as multiplier_calc

from test_all_topo_engineered_data import test_slope, test_escarp
from test_all_topo_engineered_data import mh_engineered


class TestMultiplierCalc(unittest.TestCase):

    def setUp(self):

        # A single line of elevation data to use in the tests:
        self.data_spacing = 25

    def test_multiplier_calc(self):
        cmd_folder = os.path.realpath(os.path.abspath(
                                      os.path.split(getfile(
                                                    currentframe()))[0]))

        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))

        grandparent = os.path.abspath(os.path.join(parent, os.pardir))

        if grandparent not in sys.path:
            sys.path.insert(0, grandparent)

        from topographic.multiplier_calc import multiplier_calc

        posi_neg = [100, -1000]

        for case in posi_neg:

            test_line_total = np.empty(0)
            mh_engineered_total = np.empty(0)

            # get the test line and engineered mh total of 28 test cases
            for i in range(1, len(test_slope)+1):
                print '\ntest ' + str(i) + ' ...'

                test_line = np.empty(181)
                test_line.fill(case)

                Lu = 250
                L1 = max(0.36*Lu, 0.4*test_slope[i]*500)
                L2_upper = 4*L1

                if test_escarp[i] == 'Y':
                    L2_down = 2.5*L2_upper
                else:
                    L2_down = L2_upper

                # starting position of 2Lu
                start_ind = 41

                for j in range(start_ind, 61):
                    # distance from the point to the crest
                    distance = 1500 - j*self.data_spacing
                    # updated eleveation considering the forward slope
                    test_line[j] = test_line[j] + (500-distance)*test_slope[i]
                if test_escarp[i] == 'Y':
                    for j in range(61, int(np.floor(L2_down/self.data_spacing))+61):
                        test_line[j] = test_line[60]
                else:
                    for j in range(61, 81):
                        test_line[j] = test_line[60 - (j - 60)]

                test_line_total = np.concatenate([test_line_total.flatten(),
                                                  test_line.flatten()])
                mh_engineered_total = np.concatenate([mh_engineered_total.flatten(),
                                                      mh_engineered[i].flatten()])

            # plot the line profile
            # point_no = len(test_slope)*181
            # x = np.arange(point_no)
            # y = test_line_total
            # pyplot.plot(x, y, 'g')
            # pyplot.show()

            # get the computed mh from scripts using the test line total
            mh_scripts = multiplier_calc(test_line_total, self.data_spacing)

            # get the selected points matching the tests
            mh_scripts_selection_total = np.empty(0)
            for i in range(1, len(test_slope)+1):

                mh_scripts_selection = np.concatenate([mh_scripts[0+181*(i-1)], mh_scripts[10+181*(i-1)], mh_scripts[20+181*(i-1)], mh_scripts[30+181*(i-1):33+181*(i-1)].flatten(),\
                                                       mh_scripts[40+181*(i-1)], mh_scripts[44+181*(i-1):73+181*(i-1)].flatten(), mh_scripts[80+181*(i-1)], mh_scripts[100+181*(i-1)],\
                                                       mh_scripts[120+181*(i-1)], mh_scripts[180+181*(i-1)]])

                mh_scripts_selection_total = np.concatenate([mh_scripts_selection_total.flatten(), mh_scripts_selection.flatten()])

            # assert_almost_equal(mh_engineered_total,
            #                     mh_scripts_selection_total, decimal=2,
            #                     err_msg='',verbose=True)
            assert_allclose(mh_scripts_selection_total, mh_engineered_total,
                            rtol=0.04, atol=0, err_msg='', verbose=True)


if __name__ == "__main__":
    unittest.main()
