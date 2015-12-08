"""
    Title: test_point_c.py
    Author: Tina Yang, tina.yang@ga.gov.au
    CreationDate: 2015-07-02
    Description: Unit testing module for POINT_C dictionary in value_lookup.py
"""

import sys
import os.path
import unittest
from inspect import getfile, currentframe


class TestPointC(unittest.TestCase):

    def test_point_c(self):

        cmd_folder = os.path.realpath(os.path.abspath(
                                      os.path.split(getfile(
                                                    currentframe()))[0]))

        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))

        if parent not in sys.path:
            sys.path.insert(0, parent)

        from utilities.value_lookup import ALL_NEIGHB, POINT_C

        rows = 10
        cols = 10

        i_list = [1, 3, 5, 7, 9]
        jj_list = [2, 4, 6, 8]
        lag_width = 1

        dire = ['w', 'e', 'n', 's', 'nw', 'ne', 'se', 'sw']

        result_expect = [0, 4, 5, 6, 7, 2, 2, 2, 2, 4, 5, 6, 7, 0, 2, 1, 0, 6,
                         7, 8, 9, 4, 4, 4, 4, 6, 7, 8, 9, 2, 1, 0, 4, 3, 2, 1,
                         8, 9, 6, 6, 6, 6, 8, 9, 4, 3, 2, 1, 6, 5, 4, 3, 8, 8,
                         8, 8, 6, 5, 4, 3, 0, 4, 5, 6, 7, 2, 2, 2, 2, 2, 2, 0,
                         4, 5, 4, 5, 6, 7, 0, 2, 1, 0, 6, 7, 8, 9, 4, 4, 4, 4,
                         4, 4, 2, 1, 6, 7, 6, 7, 8, 9, 2, 1, 0, 4, 3, 2, 1, 8,
                         9, 6, 6, 6, 6, 6, 6, 4, 3, 8, 9, 8, 9, 4, 3, 2, 1, 6,
                         5, 4, 3, 8, 8, 8, 8, 8, 8, 6, 5, 6, 5, 4, 3, 0, 4, 5,
                         6, 7, 2, 2, 2, 2, 2, 2, 2, 0, 4, 5, 6, 7, 4, 5, 6, 0,
                         2, 1, 0, 6, 7, 8, 9, 4, 4, 4, 4, 4, 4, 4, 2, 1, 0, 6,
                         7, 8, 9, 6, 7, 8, 2, 1, 0, 4, 3, 2, 1, 8, 9, 6, 6, 6,
                         6, 6, 6, 6, 4, 3, 2, 1, 8, 9, 8, 9, 4, 3, 2, 6, 5, 4,
                         3, 8, 8, 8, 8, 8, 8, 8, 6, 5, 4, 3, 6, 5, 4, 0, 4, 5,
                         6, 7, 2, 2, 2, 2, 2, 0, 4, 5, 6, 7, 4, 0, 2, 1, 0, 6,
                         7, 8, 9, 4, 4, 4, 4, 4, 2, 1, 0, 6, 7, 8, 9, 6, 2, 4,
                         3, 2, 1, 8, 9, 6, 6, 6, 6, 6, 4, 3, 2, 1, 8, 9, 8, 4,
                         6, 5, 4, 3, 8, 8, 8, 8, 8, 6, 5, 4, 3, 6, 0, 4, 5, 6,
                         7, 2, 2, 2, 2, 0, 4, 5, 6, 7, 2, 1, 0, 6, 7, 8, 9, 4,
                         4, 4, 4, 2, 1, 0, 6, 7, 8, 9, 4, 3, 2, 1, 8, 9, 6, 6,
                         6, 6, 4, 3, 2, 1, 8, 9, 6, 5, 4, 3, 8, 8, 8, 8, 6, 5,
                         4, 3]

        result = []

        for i in i_list:
            for a_j in jj_list:
                for a_dire in dire:
                    all_neighb_dir = ALL_NEIGHB[a_dire](i, a_j, rows, cols,
                                                        lag_width)

                    if all_neighb_dir < 4:
                        max_neighb_dir = all_neighb_dir
                    else:
                        max_neighb_dir = 4

                    for a_m in range(max_neighb_dir):
                        point_col = POINT_C[a_dire](a_j, a_m, lag_width)
                        result.append(point_col)

        self.assertEqual(result, result_expect)


if __name__ == "__main__":
    unittest.main()
