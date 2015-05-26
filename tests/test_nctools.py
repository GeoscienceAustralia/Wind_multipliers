"""
 Title: test_combine.py 
 Author: Tina Yang, tina.yang@ga.gov.au 
 CreationDate: 2014-06-02
 Description: Unit testing module for get_lat_lon and clip function
 in nctools.py 
 Version: $Rev$ 
 $Id$
"""

import numpy as np
import unittest
from numpy.testing import assert_almost_equal

import sys
import os.path
from inspect import getfile, currentframe



class TestNctools(unittest.TestCase):

    def setUp(self):         
        
        
            
        
        
        cmd_folder = os.path.realpath(os.path.abspath(os.path.split(getfile(currentframe()))[0]))         
        
        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))
                
        if parent not in sys.path:
            sys.path.insert(0, parent)
            
        
        
    
    def test_get_lat_lon(self):             
        from utilities.nctools import get_lat_lon  
        
        pixelwidth = 0.045
        pixelheight = 0.055
        
        extent = [145.00, -13.00, 146.00, -14.00]
        
        expect_lat = [-13.0275, -13.0825, -13.1375, -13.1925, -13.2475, 
                      -13.3025, -13.3575, -13.4125, -13.4675, -13.5225,
                      -13.5775, -13.6325, -13.6875, -13.7425, -13.7975,
                      -13.8525, -13.9075, -13.9625, -14.0175]
        
        expect_lon = [145.0225, 145.0675, 145.1125, 145.1575, 145.2025,
                      145.2475, 145.2925, 145.3375, 145.3825, 145.4275,
                      145.4725, 145.5175, 145.5625, 145.6075, 145.6525,
                      145.6975, 145.7425, 145.7875, 145.8325, 145.8775,
                      145.9225, 145.9675, 146.0125]
        
               
        lon, lat = get_lat_lon(extent, pixelwidth, pixelheight)
#        print lat
#        print lon
        
        # Check geographic transform:
        assert_almost_equal(expect_lon, lon, decimal=2)
        assert_almost_equal(expect_lat, lat, decimal=2) 
        
    
    def test_clip_array(self):             
        from utilities.nctools import clip_array 
        
        pixelwidth = 0.3
        pixelheight = 0.3
        
        x_left = 145.0
        y_upper = 13.0
        
        extent_list =[[145.40, -13.40, 146.40, -14.40], [145.20, -13.20, 146.20, -14.20],
                      [145.25, -13.25, 146.20, -14.20]]
        
        expected = np.array([[ 8,  9, 10, 11],
                             [15, 16, 17, 18],
                             [22, 23, 24, 25],
                             [29, 30, 31, 32]])

        data = np.arange(49).reshape(7, 7)        
        #print data

        for extent in extent_list:            
                   
            data_clip = clip_array(data, x_left, y_upper, pixelwidth, pixelheight, extent)
            #print data_clip
            
            # Check geographic transform:
            assert_almost_equal(expected, data_clip, decimal=2)
           
    


if __name__ == "__main__":
    unittest.main()
