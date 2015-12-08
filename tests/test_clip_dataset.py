"""
 Title: test_clip_dataset.py
 Author: Tina Yang, tina.yang@ga.gov.au
 CreationDate: 2014-06-02
 Description: Unit testing module for clip_dataset and reproject_dataset
 function in all_multipliers.py
 Version: $Rev$
 $Id$
"""

import unittest
from numpy.testing import assert_almost_equal, assert_array_equal

import sys
import os.path
from inspect import getfile, currentframe
from osgeo import gdal
from os.path import exists


class TestClip(unittest.TestCase):

    def setUp(self):

        cmd_folder = os.path.realpath(os.path.abspath(
                                      os.path.split(getfile
                                                    (currentframe()))[0]))

        self.testdata_folder = os.path.join(cmd_folder, 'test_data')

        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))

        if parent not in sys.path:
            sys.path.insert(0, parent)

    def test_clip(self):

        dem = os.path.join(self.testdata_folder, "test_raster_dem.img")
        dem_expect_result = os.path.join(self.testdata_folder,
                                         'test_raster_expect_clip_dem.img')

        lc = os.path.join(self.testdata_folder, "test_raster_lc.img")

        from all_multipliers import Multipliers

        mp = Multipliers(lc, dem)

        extent = [143.2, -23.2, 143.4, -23.4]

        scripts_result = os.path.join(self.testdata_folder,
                                      'test_raster_clip_dem.img')

        mp.open_dem()
        mp.clip_dataset(extent, scripts_result)

        assert exists(scripts_result)

        script_dataset = gdal.Open(scripts_result)
        script_band = script_dataset.GetRasterBand(1)
        script_data = script_band.ReadAsArray()

        expect_dataset = gdal.Open(dem_expect_result)
        expect_band = expect_dataset.GetRasterBand(1)
        expect_data = expect_band.ReadAsArray()

        # Check geographic transform:
        assert_almost_equal(script_dataset.GetGeoTransform(),
                            expect_dataset.GetGeoTransform(), decimal=2)

        # Check shape and content of arrays:
        self.assertEqual(script_data.shape, expect_data.shape)
        # self.assertEqual(script_data.all(), expect_data.all())
        assert_array_equal(script_data, expect_data)

        del script_dataset, expect_dataset

    def test_reproject(self):

        lc = os.path.join(self.testdata_folder, "test_raster_lc.img")
        match_ds = os.path.join(self.testdata_folder,
                                "test_raster_clip_dem.img")

        from all_multipliers import reproject_dataset

        dst_file = os.path.join(self.testdata_folder, 'test_raster_dem_lc.img')

        reproject_dataset(lc, match_ds, dst_file)

        assert exists(dst_file)

        dst_dataset = gdal.Open(dst_file)
        dst_band = dst_dataset.GetRasterBand(1)
        dst_data = dst_band.ReadAsArray()

        match_dataset = gdal.Open(match_ds)
        match_band = match_dataset.GetRasterBand(1)
        match_data = match_band.ReadAsArray()

        # Check geographic transform:
        assert_almost_equal(dst_dataset.GetGeoTransform(),
                            match_dataset.GetGeoTransform(), decimal=2)

        # Check shape
        self.assertEqual(dst_data.shape, match_data.shape)

        del dst_dataset, match_dataset


if __name__ == "__main__":
    unittest.main()
