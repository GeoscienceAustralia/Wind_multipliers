"""
    Title: test_shielding.py
    Author: Tina Yang, tina.yang@ga.gov.au
    CreationDate: 2014-05-01
    Description: Unit testing module for combine, init_kern and
    init_kern_diag functions
    in shield_mult.py
    Version: $Rev$
    $Id$
"""

import os.path
import sys
import unittest
from inspect import getfile, currentframe

import numpy as np
from numpy.testing import assert_almost_equal, assert_array_almost_equal
from osgeo import gdal

from config import configparser as config


class TestShieldingMultiplier(unittest.TestCase):

    def setUp(self):

        cmd_folder = os.path.realpath(os.path.abspath(
                                      os.path.split(getfile(
                                                    currentframe()))[0]))

        self.testdata_folder = os.path.join(cmd_folder, 'test_data')

        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))

        if parent not in sys.path:
            sys.path.insert(0, parent)

        print('finish')

    def test_combine(self):

        from shielding.shield_mult import combine

        slope_array = np.array([[0.2, 0.4, 4, 5, 13, 11],
                                [7, 14, 3, 1, 8, 6],
                                [1.8, 9, 4, 7, 2, 18],
                                [2, 5, 15, 12, 7, 8],
                                [3.6, 8, 3, 1, 5, 2],
                                [2.8, 9.6, 4, 15, 1, 3]])

        aspect_array = np.array([[1, 2, 3, 4, 5, 5],
                                 [7, 5, 3, 1, 8, 6],
                                 [7, 7, 4, 7, 2, 7],
                                 [2, 5, 7, 7, 7, 8],
                                 [7, 8, 3, 1, 5, 2],
                                 [7, 7, 4, 7, 1, 3]])

        ms_orig_array = np.array([[0.18, 0.36, 0.36, 0.45, 0.98, 0.85],
                                  [0.74, 0.94, 0.27, 0.09, 0.82, 0.92],
                                  [0.78, 0.93, 0.36, 0.77, 0.23, 0.98],
                                  [0.22, 0.58, 0.85, 0.28, 0.77, 0.83],
                                  [0.65, 0.84, 0.92, 0.89, 0.75, 0.82],
                                  [0.89, 0.96, 0.45, 0.85, 0.93, 0.38]])

        one_dir = 'w'

        scripts_result = combine(ms_orig_array, slope_array, aspect_array,
                                 one_dir)

        np.set_printoptions(precision=2)

        expect_result = np.array([[0.16, 0.32, 0.32, 0.41, 0.96, 0.77],
                                  [0.76, 0.88, 0.24, 0.08, 0.74, 0.85],
                                  [0.70, 0.95, 0.32, 0.78, 0.21, 1],
                                  [0.20, 0.52, 1, 0.95, 0.78, 0.75],
                                  [0.60, 0.76, 0.85, 0.80, 0.68, 0.74],
                                  [0.80, 0.98, 0.41, 1, 0.86, 0.34]])

        assert_almost_equal(scripts_result, expect_result, decimal=2,
                            err_msg='', verbose=True)

    def test_combine_scenario(self):

        # A single line of elevation data to use in the tests:
        pixelwidth = 25.
        ms_orig = np.ones([3, 640])
        ms_orig[:, 160:200] = 0.85
        ms_orig[:, 200:240] = 0.9
        ms_orig[:, 320:360] = 0.85
        ms_orig[:, 360:400] = 0.88
        ms_orig[:, 400:440] = 0.9
        ms_orig[:, 520:560] = 0.85
        ms_orig[:, 560:600] = 0.88

        slope_array = np.zeros([3, 640])
        slope_array[:, 320:360] = 3.44
        slope_array[:, 360:400] = 3.44
        slope_array[:, 520:560] = 12.68
        slope_array[:, 560:600] = 12.68

        aspect_array = np.empty([3, 640])
        aspect_array.fill(9)
        aspect_array[:, 320:360] = 7
        aspect_array[:, 360:400] = 3
        aspect_array[:, 520:560] = 7
        aspect_array[:, 560:600] = 3

        ms_engineered = np.ones(640)
        ms_engineered[161] = 0.957
        ms_engineered[162] = 0.836
        ms_engineered[163:201] = 0.765
        ms_engineered[201] = 0.771
        ms_engineered[202] = 0.791
        ms_engineered[203:241] = 0.810
        ms_engineered[241] = 0.836
        ms_engineered[242] = 0.916
        ms_engineered[243:321] = 1.0
        ms_engineered[321] = 0.959
        ms_engineered[322] = 0.841
        ms_engineered[323:360] = 0.769
        ms_engineered[360] = 0.765
        ms_engineered[361] = 0.769
        ms_engineered[362] = 0.782
        ms_engineered[363:401] = 0.792
        ms_engineered[401] = 0.795
        ms_engineered[402] = 0.803
        ms_engineered[403:441] = 0.810
        ms_engineered[441] = 0.836
        ms_engineered[442] = 0.916
        ms_engineered[443:560] = 1.0
        ms_engineered[560] = 0.765
        ms_engineered[561] = 0.769
        ms_engineered[562] = 0.782
        ms_engineered[563:601] = 0.792
        ms_engineered[601] = 0.806
        ms_engineered[602] = 0.912
        ms_engineered[603:640] = 1.0

        from shielding.shield_mult import kern_w, blur_image, combine

        kernel_size = int(100.0 / pixelwidth) - 1

        if kernel_size > 0:
            outdata = np.zeros_like(ms_orig, dtype=np.float32)
            mask = kern_w(kernel_size)
            outdata = blur_image(ms_orig, mask)
        else:
            outdata = ms_orig

        result = combine(outdata, slope_array, aspect_array, 'w')

        # get the computed mz from scripts using the test line total
        mh_scripts = result[1, :].flatten()
        np.set_printoptions(precision=3)

        assert_almost_equal(mh_scripts, ms_engineered, decimal=2, err_msg='',
                            verbose=True)

    def test_init_kern(self):

        from shielding.shield_mult import init_kern, init_kern_diag

        init_kernel_expect = np.array([[0., 0., 0., 0., 0., 0., 0.],
                                       [0., 0., 0., 0., 0., 0., 0.],
                                       [0., 0., 0., 0., 0., 0., 0.],
                                       [0., 0., 0., 0., 0., 0., 0.],
                                       [0., 0., 0., 0.143, 0., 0., 0.],
                                       [0., 0., 0.143, 0.143, 0.143, 0., 0.],
                                       [0., 0., 0.143, 0.143, 0.143, 0., 0.]])

        init_kernel_diag_expect = np.array([[0., 0., 0., 0., 0.167, 0., 0.],
                                            [0., 0., 0., 0., 0.167, 0.167, 0.],
                                            [0., 0., 0., 0., 0.167, 0.167,
                                             0.167],
                                            [0., 0., 0., 0., 0., 0., 0.],
                                            [0., 0., 0., 0., 0., 0., 0.],
                                            [0., 0., 0., 0., 0., 0., 0.],
                                            [0., 0., 0., 0., 0., 0., 0.]])

        kernel_size = 3

        init_kernel = init_kern(kernel_size)
        init_kernel_diag = init_kern_diag(kernel_size)

        assert_almost_equal(init_kernel, init_kernel_expect, decimal=2,
                            err_msg='', verbose=True)
        assert_almost_equal(init_kernel_diag, init_kernel_diag_expect,
                            decimal=2, err_msg='', verbose=True)

    def test_kern_e(self):

        from shielding.shield_mult import kern_e

        kernel_e_expect = np.array([[0., 0., 0., 0., 0., 0., 0.],
                                    [0., 0., 0., 0., 0., 0., 0.],
                                    [0.143, 0.143, 0., 0., 0., 0., 0.],
                                    [0.143, 0.143, 0.143, 0., 0., 0., 0.],
                                    [0.143, 0.143, 0., 0., 0., 0., 0.],
                                    [0., 0., 0., 0., 0., 0., 0.],
                                    [0., 0., 0., 0., 0., 0., 0.]])

        kernel_size = 3

        kernel_e = kern_e(kernel_size)

        assert_almost_equal(kernel_e, kernel_e_expect, decimal=2, err_msg='',
                            verbose=True)

    def test_kern_w(self):

        from shielding.shield_mult import kern_w

        kernel_w_expect = np.array([[0., 0., 0., 0., 0., 0., 0.],
                                    [0., 0., 0., 0., 0., 0., 0.],
                                    [0., 0., 0., 0., 0., 0.143, 0.143],
                                    [0., 0., 0., 0., 0.143, 0.143, 0.143],
                                    [0., 0., 0., 0., 0., 0.143, 0.143],
                                    [0., 0., 0., 0., 0., 0., 0.],
                                    [0., 0., 0., 0., 0., 0., 0.]])

        kernel_size = 3

        kernel_w = kern_w(kernel_size)

        assert_almost_equal(kernel_w, kernel_w_expect, decimal=2, err_msg='',
                            verbose=True)

    def test_kern_n(self):

        from shielding.shield_mult import kern_n

        kernel_n_expect = np.array([[0., 0., 0., 0., 0., 0., 0.],
                                    [0., 0., 0., 0., 0., 0., 0.],
                                    [0., 0., 0., 0., 0., 0., 0.],
                                    [0., 0., 0., 0., 0., 0., 0.],
                                    [0., 0., 0., 0.143, 0., 0., 0.],
                                    [0., 0., 0.143, 0.143, 0.143, 0., 0.],
                                    [0., 0., 0.143, 0.143, 0.143, 0., 0.]])

        kernel_size = 3

        kernel_n = kern_n(kernel_size)

        assert_almost_equal(kernel_n, kernel_n_expect, decimal=2, err_msg='',
                            verbose=True)

    def test_kern_s(self):

        from shielding.shield_mult import kern_s

        kernel_s_expect = np.array([[0., 0., 0.143, 0.143, 0.143, 0., 0.],
                                    [0., 0., 0.143, 0.143, 0.143, 0., 0.],
                                    [0., 0., 0., 0.143, 0., 0., 0.],
                                    [0., 0., 0., 0., 0., 0., 0.],
                                    [0., 0., 0., 0., 0., 0., 0.],
                                    [0., 0., 0., 0., 0., 0., 0.],
                                    [0., 0., 0., 0., 0., 0., 0.]])

        kernel_size = 3

        kernel_s = kern_s(kernel_size)

        assert_almost_equal(kernel_s, kernel_s_expect, decimal=2, err_msg='',
                            verbose=True)

    def test_sw(self):

        from shielding.shield_mult import kern_sw

        kernel_sw_expect = np.array([[0., 0., 0., 0., 0.167, 0., 0.],
                                     [0., 0., 0., 0., 0.167, 0.167, 0.],
                                     [0., 0., 0., 0., 0.167, 0.167, 0.167],
                                     [0., 0., 0., 0., 0., 0., 0.],
                                     [0., 0., 0., 0., 0., 0., 0.],
                                     [0., 0., 0., 0., 0., 0., 0.],
                                     [0., 0., 0., 0., 0., 0., 0.]])

        kernel_size = 3

        kernel_sw = kern_sw(kernel_size)

        assert_almost_equal(kernel_sw, kernel_sw_expect, decimal=2, err_msg='',
                            verbose=True)

    def test_ne(self):

        from shielding.shield_mult import kern_ne

        kernel_ne_expect = np.array([[0., 0., 0., 0., 0., 0., 0.],
                                     [0., 0., 0., 0., 0., 0., 0.],
                                     [0., 0., 0., 0., 0., 0., 0.],
                                     [0., 0., 0., 0., 0., 0., 0.],
                                     [0.167, 0.167, 0.167, 0., 0., 0., 0.],
                                     [0., 0.167, 0.167, 0., 0., 0., 0.],
                                     [0., 0., 0.167, 0., 0., 0., 0.]])

        kernel_size = 3

        kernel_ne = kern_ne(kernel_size)

        assert_almost_equal(kernel_ne, kernel_ne_expect, decimal=2, err_msg='',
                            verbose=True)

    def test_nw(self):

        from shielding.shield_mult import kern_nw

        kernel_nw_expect = np.array([[0., 0., 0., 0., 0., 0., 0.],
                                     [0., 0., 0., 0., 0., 0., 0.],
                                     [0., 0., 0., 0., 0., 0., 0.],
                                     [0., 0., 0., 0., 0., 0., 0.],
                                     [0., 0., 0., 0., 0.167, 0.167, 0.167],
                                     [0., 0., 0., 0., 0.167, 0.167, 0.],
                                     [0., 0., 0., 0., 0.167, 0., 0.]])

        kernel_size = 3

        kernel_nw = kern_nw(kernel_size)

        assert_almost_equal(kernel_nw, kernel_nw_expect, decimal=2, err_msg='',
                            verbose=True)

    def test_se(self):

        from shielding.shield_mult import kern_se

        kernel_se_expect = np.array([[0., 0., 0.167, 0., 0., 0., 0.],
                                     [0., 0.167, 0.167, 0., 0., 0., 0.],
                                     [0.167, 0.167, 0.167, 0., 0., 0., 0.],
                                     [0., 0., 0., 0., 0., 0., 0.],
                                     [0., 0., 0., 0., 0., 0., 0.],
                                     [0., 0., 0., 0., 0., 0., 0.],
                                     [0., 0., 0., 0., 0., 0., 0.]])

        kernel_size = 3

        kernel_se = kern_se(kernel_size)

        assert_almost_equal(kernel_se, kernel_se_expect, decimal=2, err_msg='',
                            verbose=True)

    def test_get_slope_aspect(self):

        dem = os.path.join(self.testdata_folder, "dem_4_slope.img")
        slope_expect = os.path.join(self.testdata_folder, "slope.img")
        aspect_expect = os.path.join(self.testdata_folder, "aspect.img")

        slope_dataset = gdal.Open(slope_expect)
        dst_band = slope_dataset.GetRasterBand(1)
        slope_array_expect = dst_band.ReadAsArray()

        aspect_dataset = gdal.Open(aspect_expect)
        dst_band = aspect_dataset.GetRasterBand(1)
        aspect_array_expect = dst_band.ReadAsArray()

        from shielding.shield_mult import get_slope_aspect

        slope_array, aspect_array = get_slope_aspect(dem)

        # Check shape and content of arrays:
        assert_array_almost_equal(slope_array, slope_array_expect, decimal=0,
                                  err_msg='', verbose=True)

        assert_array_almost_equal(aspect_array, aspect_array_expect,
                                  decimal=-1, err_msg='', verbose=True)

    def test_terrain_class2ms_orig(self):

        config.set('inputValues', 'terrain_table', os.path.join(self.testdata_folder, 'terrain_classification.csv'))

        terrain = os.path.join(self.testdata_folder, "lc_terrain.img")

        ms_orig_expect = os.path.join(self.testdata_folder,
                                      "lc_terrain_ms_expect.img")
        ms_orig_dataset_expect = gdal.Open(ms_orig_expect)
        dst_band = ms_orig_dataset_expect.GetRasterBand(1)
        ms_orig_array_expect = dst_band.ReadAsArray()

        from shielding.shield_mult import terrain_class2ms_orig

        ms_orig = terrain_class2ms_orig(terrain)
        ms_orig_dataset = gdal.Open(ms_orig)
        dst_band = ms_orig_dataset.GetRasterBand(1)
        ms_orig_array = dst_band.ReadAsArray()

        # Check geographic transform:
        assert_almost_equal(ms_orig_dataset_expect.GetGeoTransform(),
                            ms_orig_dataset.GetGeoTransform(), decimal=2)

        # Check shape and content of arrays:
        assert_array_almost_equal(ms_orig_array_expect, ms_orig_array,
                                  decimal=0, err_msg='', verbose=True)

        del ms_orig_dataset_expect, ms_orig_dataset


if __name__ == "__main__":
    unittest.main()
