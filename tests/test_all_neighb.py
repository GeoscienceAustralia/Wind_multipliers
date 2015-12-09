"""
    Title: test_all_neighb.py
    Author: Tina Yang, tina.yang@ga.gov.au
    CreationDate: 2015-07-02
    Description: Unit testing for ALL_NEIGHB dictionary in value_lookup.py
"""

import sys
import os.path
import unittest
from inspect import getfile, currentframe


class TestAllNEIGHB(unittest.TestCase):

    def test_all_neighb(self):

        cmd_folder = os.path.realpath(os.path.abspath(
                                      os.path.split(getfile
                                                    (currentframe()))[0]))

        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))

        if parent not in sys.path:
            sys.path.insert(0, parent)

        from utilities.value_lookup import ALL_NEIGHB

        rows = 10
        cols = 10

        i_list = [1, 3, 5, 7, 9]
        jj_list = [2, 4, 5, 6, 8]
        lag_width = 1

        dire = ['w', 'e', 'n', 's', 'nw', 'ne', 'se', 'sw']

        result_expect = [1, 6, 0, 7, 0, 0, 6, 1, 3, 4, 0, 7, 0, 0, 4, 3, 4, 3,
                         0, 7, 0, 0, 3, 4, 5, 2, 0, 7, 0, 0, 2, 5, 7, 0, 0, 7,
                         0, 0, 0, 7, 1, 6, 2, 5, 1, 2, 5, 1, 3, 4, 2, 5, 2, 2,
                         4, 3, 4, 3, 2, 5, 2, 2, 3, 4, 5, 2, 2, 5, 2, 2, 2, 5,
                         7, 0, 2, 5, 2, 0, 0, 5, 1, 6, 4, 3, 1, 4, 3, 1, 3, 4,
                         4, 3, 3, 4, 3, 3, 4, 3, 4, 3, 4, 3, 3, 3, 5, 2, 4, 3,
                         4, 2, 2, 3, 7, 0, 4, 3, 4, 0, 0, 3, 1, 6, 6, 1, 1, 6,
                         1, 1, 3, 4, 6, 1, 3, 4, 1, 1, 4, 3, 6, 1, 4, 3, 1, 1,
                         5, 2, 6, 1, 5, 2, 1, 1, 7, 0, 6, 1, 6, 0, 0, 1, 1, 6,
                         8, -1, 1, 6, -1, -1, 3, 4, 8, -1, 3, 4, -1, -1, 4, 3,
                         8, -1, 4, 3, -1, -1, 5, 2, 8, -1, 5, 2, -1, -1, 7, 0,
                         8, -1, 7, 0, -1, -1]

        result = []

        for i in i_list:
            for a_j in jj_list:
                for one_dir in dire:
                    neig = ALL_NEIGHB[one_dir](i, a_j, rows, cols, lag_width)
                    result.append(neig)

        self.assertEqual(result, result_expect)


if __name__ == "__main__":
    unittest.main()
