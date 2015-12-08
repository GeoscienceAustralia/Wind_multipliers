"""
    Title: test_conservatism.py
    Author: Tina Yang, tina.yang@ga.gov.au
    CreationDate: 2015-11-20
    Description: Unit testing module for remove_conservatism function in
                 topo_mult.py
    Version: $Rev$
    $Id$
"""

import sys
import os.path
import unittest
import numpy as np
from numpy.testing import assert_allclose
from inspect import getfile, currentframe


class TestRemove_Conservatism(unittest.TestCase):

    def test_remove_conservatism(self):
        cmd_folder = os.path.realpath(os.path.abspath(
                                      os.path.split(getfile(
                                                    currentframe()))[0]))

        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))

        grandparent = os.path.abspath(os.path.join(parent, os.pardir))

        if grandparent not in sys.path:
            sys.path.insert(0, grandparent)

        from topographic.topo_mult import remove_conservatism

        mh_cons_expect = np.array([[1.0, 1.0725, 1.14, 1.2025, 1.26, 1.35,
                                    1.44, 1.53],
                                   [1.53, 1., 1.0725, 1.14, 1.2025, 1.26, 1.35,
                                    1.44],
                                   [1.35, 1.44, 1.0, 1.0725, 1.14, 1.2025,
                                    1.26, 1.35],
                                   [1.53, 1.26, 1.2025, 1.0, 1.0725, 1.14,
                                    1.2025, 1.26],
                                   [1.44, 1.53, 1.53, 1.26, 1.0, 1.0725, 1.14,
                                    1.2025],
                                   [1.35, 1.44, 1.53, 1.44, 1.35,  1.0, 1.0725,
                                    1.14],
                                   [1.26, 1.35, 1.44, 1.53, 1.14, 1.2025, 1.0,
                                    1.0725],
                                   [1.2025, 1.26, 1.35, 1.44, 1.53, 1.2025,
                                    1.14, 1.0]])

        mhdata = np.array([[1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7],
                           [1.7, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6],
                           [1.5, 1.6, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5],
                           [1.7, 1.4, 1.3, 1.0, 1.1, 1.2, 1.3, 1.4],
                           [1.6, 1.7, 1.7, 1.4, 1.0, 1.1, 1.2, 1.3],
                           [1.5, 1.6, 1.7, 1.6, 1.5, 1.0, 1.1, 1.2],
                           [1.4, 1.5, 1.6, 1.7, 1.2, 1.3, 1.0, 1.1],
                           [1.3, 1.4, 1.5, 1.6, 1.7, 1.3, 1.2, 1.0]])

        mh_cons_scripts = remove_conservatism(mhdata)

        assert_allclose(mh_cons_scripts, mh_cons_expect, rtol=0.04, atol=0,
                        err_msg='', verbose=True)


if __name__ == "__main__":
    unittest.main()
