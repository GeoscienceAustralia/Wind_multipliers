"""
    Title: test_findpeaks.py
    Author: Tina Yang, tina.yang@ga.gov.au
    CreationDate: 2014-05-01
    Description: Unit testing module for findpeaks function in findpeaks.py
    Version: $Rev$
    $Id$
"""

import sys
import os.path
import unittest
import numpy as np
from numpy.testing import assert_almost_equal
from matplotlib import pyplot
import logging as log
from test_all_topo_engineered_data import test_line, expect_results
from inspect import getfile, currentframe


def escarpment_factor(profile, ridge, valley, data_spacing):
    """
    Calculate escarpment factor
    """

    max_escarp = 3
    min_escarp = 0.5
    nrow = np.size(profile)

    H = profile[ridge] - profile[valley]
    Lu = abs(ridge - valley) * data_spacing / 2
    slope = H / (2 * Lu)
    beta_ind = int(np.minimum(nrow - 1, np.floor(ridge + (2 * Lu / data_spacing))))
    H_r2beta = profile[ridge] - profile[beta_ind]
    D_r2beta = (beta_ind - ridge) * data_spacing
    if D_r2beta > 0:                 # D_r2beta can be 0, 25, 50, ...
        slope_r2mL2 = H_r2beta/D_r2beta

        # when a symmetrical ridge slope_r2mL2=slope so escarp_factor=1
        # If slope_r2mL2=0, escarp_factor=2.5
        escarp_factor = 2.5 - 1.5 * slope_r2mL2 / slope

        if escarp_factor < min_escarp:
            escarp_factor = min_escarp
        elif escarp_factor > max_escarp:
            escarp_factor = max_escarp

    else:      # the ridge is on the end
        slope_r2mL2 = 999
        escarp_factor = 1

    return H, slope, slope_r2mL2, escarp_factor


class TestFindpeaks(unittest.TestCase):

    def setUp(self):

        self.data_spacing = 25

    def test_findpeaks(self):

        cmd_folder = os.path.realpath(os.path.abspath(
                                      os.path.split(getfile(
                                                    currentframe()))[0]))

        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))

        grandparent = os.path.abspath(os.path.join(parent, os.pardir))

        if grandparent not in sys.path:
            sys.path.insert(0, grandparent)

        from topographic.findpeaks import findpeaks, findvalleys

        # test for each scenerio
        # for p in range(3, 4):
        for p in range(1, len(test_line)+1):
            print '\ntest ' + str(p) + ' ...'
            nrow = np.size(test_line[p])

            # take the largest integer of each element of the data line
            fwd_line = np.floor(test_line[p])

            # Get the indices of the ridges & valleys
            ridge_ind = findpeaks(fwd_line)        # relative ind
            valley_ind = findvalleys(fwd_line)    # relative ind

            print ridge_ind
            print valley_ind

            nrow = np.size(ridge_ind)
            H = np.ones((nrow, 1), dtype=float)
            slope = np.ones((nrow, 1), dtype=float)
            downwind_slope = np.ones((nrow, 1), dtype=float)
            escarp_factor = np.ones((nrow, 1), dtype=float)

            if np.size(ridge_ind) == 0:  # the DEM is completely flat
                log.debug("Flat line")

            # the DEM is downward slope all the time
            elif np.size(ridge_ind) == 1 and ridge_ind[0] == 0:
                log.debug("Downward slope")

            else:                # 2 general cases, calculate m, works as Mh.m

                if ridge_ind[0] == 0:    # (1) down up down up ....
                    for i in range(1, np.size(ridge_ind)):
                        H[i], slope[i], downwind_slope[i], escarp_factor[i] = \
                        escarpment_factor(fwd_line, ridge_ind[i],
                                          valley_ind[i-1],
                                          self.data_spacing)

                else:                    # (2) up dowm up dowm ....
                    for i in range(0, np.size(ridge_ind)):
                        H[i], slope[i], downwind_slope[i], escarp_factor[i] = \
                        escarpment_factor(fwd_line, ridge_ind[i],
                                          valley_ind[i], self.data_spacing)

            hill_no = np.size(ridge_ind)

            scripts_result = np.concatenate([[hill_no], H.flatten(),
                                             slope.flatten(),
                                            downwind_slope.flatten(),
                                            escarp_factor.flatten()])

            print scripts_result
            print expect_results[p]

            assert_almost_equal(scripts_result, expect_results[p], decimal=2,
                                err_msg='', verbose=True)


if __name__ == "__main__":
    unittest.main()
