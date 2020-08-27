"""
 Title: test_openFiles.py
 Author: Claire Krause, claire.krause@ga.gov.au
 CreationDate: 2017-08-30
 Description: Unit testing module for opening landcover and DEM datasets

 Version:

 ModifiedBy:
 ModifiedDate:
 Modification:

 $Id:
"""

import sys
import os.path
import unittest
from inspect import getfile, currentframe
from all_multipliers import Multipliers
from utilities.files import fl_start_log


class TestOpenFiles(unittest.TestCase):

    def setUp(self):
        cmd_folder = os.path.realpath(os.path.abspath(
                                      os.path.split(getfile(
                                                    currentframe()))[0]))
        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))
        if parent not in sys.path:
            sys.path.insert(0, parent)
        testdata_folder = os.path.join(cmd_folder, 'test_data')
        self.dem = os.path.join(testdata_folder, 'dem_4_slope.img')
        self.baddem = os.path.join(testdata_folder, 'dem_missing_slope.img')
        self.tifdem = os.path.join(testdata_folder, 'test_gtiff.tif')
        self.lcv = os.path.join(testdata_folder, 'test_raster_lc.img')
        self.mult = Multipliers(self.lcv, self.dem)
        self.badmult = Multipliers(self.lcv, self.baddem)
        self.gtiffMult = Multipliers(self.lcv, self.tifdem)

    def test_DEM_open(self):
        """Test the DEM file is being opened properly"""
        self.mult.open_dem()
        #(test for self attribute)
        self.assertTrue(hasattr(self.mult, 'dem_type'))
        
    def test_bodgy_DEM(self):
        """Test the DEM file opening fails properly"""
        self.assertRaises(OSError, self.badmult.open_dem)
    
    def test_GTiff_open(self):
        """Test function can open GeoTiff"""
        self.gtiffMult.open_dem()
        self.assertTrue(hasattr(self.gtiffMult, 'dem_type'))
    
if __name__ == "__main__":
    fl_start_log('', 'CRITICAL', False)
    testSuite = unittest.makeSuite(TestGPD,'test')
    unittest.TextTestRunner(verbosity=3).run(testSuite)
