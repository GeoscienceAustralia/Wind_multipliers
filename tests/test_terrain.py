"""
    Title: test_terrain.py
    Author: Tina Yang, tina.yang@ga.gov.au
    CreationDate: 2014-05-01
    Updated: May 2017, Claire Krause
    Description: Unit testing module for convo function in
                 terrain_mult.py
    Version: $Rev$
    $Id$
"""

import sys
import os.path
import unittest
import numpy as np
from numpy.testing import assert_almost_equal, assert_array_almost_equal
from inspect import getfile, currentframe
from osgeo import gdal
import pandas as pd

class TestTerrainMultiplier(unittest.TestCase):

    def setUp(self):

        cmd_folder = os.path.realpath(os.path.abspath(
                                      os.path.split(getfile(
                                                    currentframe()))[0]))

        self.testdata_folder = os.path.join(cmd_folder, 'test_data')

        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))

        if parent not in sys.path:
            sys.path.insert(0, parent)

    def test_terrain_class2mz_orig(self):

        from terrain.terrain_mult import terrain_class2mz_orig

        data = np.array([[1000, 1000, 949, 898],
                         [898,  1063, 774, 949],
                         [949,  774,  806, 806],
                         [1063, 1000, 949, 774],
                         [1000, 898,  774, 949],
                         [949,  1063, 806, 774]])
        mz_init = pd.DataFrame({'CATEGORY' : pd.Series([774, 806, 898, 949, 1000, 1063], 
                                                       index = [0, 1, 2, 3, 4, 5]),
                                'ROUGHNESS_LENGTH_m' : pd.Series([1, 0.4, 0.08, 0.04, 0.02, 0.006], 
                                                       index = [0, 1, 2, 3, 4, 5])})

        scripts_result = terrain_class2mz_orig(data, mz_init)

        np.set_printoptions(precision=3)

        expect_result = np.array([[ 0.8870,  0.8870,  0.8447,  0.8078],
                                  [ 0.8078,  0.9802,  0.7037,  0.8447],
                                  [ 0.8447,  0.7037,  0.7372,  0.7372],
                                  [ 0.9802,  0.8870,  0.8447,  0.7037],
                                  [ 0.8870,  0.8078,  0.7037 , 0.8447],
                                  [ 0.8447,  0.9802,  0.7372,  0.7037]])

        assert_almost_equal(scripts_result, expect_result, decimal=3,
                            err_msg='', verbose=True)

    def test_convo(self):

        Mz_exp_w = np.array([[0., 1., 2., 0., 0.5, 1., 1.5, 2.5],
                             [8., 9., 10., 8., 8.5, 9., 9.5, 10.5],
                             [16., 17., 18., 16., 16.5, 17., 17.5, 18.5],
                             [24., 25., 26., 24., 24.5, 25., 25.5, 26.5],
                             [32., 33., 34., 32., 32.5, 33., 33.5, 34.5],
                             [40., 41., 42., 40., 40.5, 41., 41.5, 42.5],
                             [48., 49., 50., 48., 48.5, 49., 49.5, 50.5],
                             [56., 57., 58., 56., 56.5, 57., 57.5, 58.5]])

        Mz_exp_e = np.array([[4.5, 5.5, 6., 6.5, 7., 5., 6., 7.],
                             [12.5, 13.5, 14., 14.5, 15., 13., 14., 15.],
                             [20.5, 21.5, 22., 22.5, 23., 21., 22., 23.],
                             [28.5, 29.5, 30., 30.5, 31., 29., 30., 31.],
                             [36.5, 37.5, 38., 38.5, 39., 37., 38., 39.],
                             [44.5, 45.5, 46., 46.5, 47., 45., 46., 47.],
                             [52.5, 53.5, 54., 54.5, 55., 53., 54., 55.],
                             [60.5, 61.5, 62., 62.5, 63., 61., 62., 63.]])

        Mz_exp_n = np.array([[0., 1., 2., 3., 4., 5., 6., 7.],
                             [8., 9., 10., 11., 12., 13., 14., 15.],
                             [16., 17., 18., 19., 20., 21., 22., 23.],
                             [0., 1., 2., 3., 4., 5., 6., 7.],
                             [4., 5., 6., 7., 8., 9., 10., 11.],
                             [8., 9., 10., 11., 12., 13., 14., 15.],
                             [12., 13., 14., 15., 16., 17., 18., 19.],
                             [20., 21., 22., 23., 24., 25., 26., 27.]])

        Mz_exp_s = np.array([[36.,  37.,  38.,  39.,  40.,  41.,  42.,  43.],
                             [44.,  45.,  46.,  47.,  48.,  49.,  50.,  51.],
                             [48.,  49.,  50.,  51.,  52.,  53.,  54.,  55.],
                             [52.,  53.,  54.,  55.,  56.,  57.,  58.,  59.],
                             [56.,  57.,  58.,  59.,  60.,  61.,  62.,  63.],
                             [40.,  41.,  42.,  43.,  44.,  45.,  46.,  47.],
                             [48.,  49.,  50.,  51.,  52.,  53.,  54.,  55.],
                             [56.,  57.,  58.,  59.,  60.,  61.,  62.,  63.]])

        Mz_exp_nw = np.array([[0., 1., 2., 3., 4., 5., 6., 7.],
                              [8., 9., 10., 11., 12., 13., 14., 15.],
                              [16., 17., 18., 19., 20., 21., 22., 23.],
                              [24., 25., 26., 0., 1., 2., 3., 4.],
                              [32., 33., 34., 8., 4.5, 5.5, 6.5, 7.5],
                              [40., 41., 42., 16., 12.5, 9., 10., 11.],
                              [48., 49., 50., 24., 20.5, 17., 13.5, 14.5],
                              [56., 57., 58., 32., 28.5, 25., 21.5, 22.5]])

        Mz_exp_ne = np.array([[0., 1., 2., 3., 4., 5., 6., 7.],
                              [8., 9., 10., 11., 12., 13., 14., 15.],
                              [16., 17., 18., 19., 20., 21., 22., 23.],
                              [3., 4., 5., 6., 7., 29., 30., 31.],
                              [7.5, 8.5, 9.5, 10.5, 15., 37., 38., 39.],
                              [12., 13., 14., 18.5, 23., 45., 46., 47.],
                              [16.5, 17.5, 22., 26.5, 31., 53., 54., 55.],
                              [24.5, 25.5, 30., 34.5, 39., 61., 62., 63.]])

        Mz_exp_se = np.array([[40.5, 41.5, 38., 34.5, 31., 5., 6., 7.],
                              [48.5, 49.5, 46., 42.5, 39., 13., 14., 15.],
                              [52., 53., 54., 50.5, 47., 21., 22., 23.],
                              [55.5, 56.5, 57.5, 58.5, 55., 29., 30., 31.],
                              [59., 60., 61., 62., 63., 37., 38., 39.],
                              [40., 41., 42., 43., 44., 45., 46., 47.],
                              [48., 49., 50., 51., 52., 53., 54., 55.],
                              [56., 57., 58., 59., 60., 61., 62., 63.]])

        Mz_exp_sw = np.array([[0., 1., 2., 24., 28.5, 33., 37.5, 38.5],
                              [8., 9., 10., 32., 36.5, 41., 45.5, 46.5],
                              [16., 17., 18., 40., 44.5, 49., 50., 51.],
                              [24., 25., 26., 48., 52.5, 53.5, 54.5, 55.5],
                              [32., 33., 34., 56., 57., 58., 59., 60.],
                              [40., 41., 42., 43., 44., 45., 46., 47.],
                              [48., 49., 50., 51., 52., 53., 54., 55.],
                              [56., 57., 58., 59., 60., 61., 62., 63.]])

        result_list = [Mz_exp_w, Mz_exp_e, Mz_exp_n, Mz_exp_s, Mz_exp_nw,
                       Mz_exp_ne, Mz_exp_se, Mz_exp_sw]

        from terrain.terrain_mult import convo

        data = np.arange(64).reshape(8, 8)
        avg_width = 4
        lag_width = 2

        dire = ['w', 'e', 'n', 's', 'nw', 'ne', 'se', 'sw']

        index = 0

        for one_dir in dire:

            outdata = convo(one_dir, data, avg_width, lag_width)

            Mz_exp = result_list[index]

            assert_almost_equal(outdata,  Mz_exp, decimal=2, err_msg='',
                                verbose=True)

            index += 1


if __name__ == "__main__":
    unittest.main()
