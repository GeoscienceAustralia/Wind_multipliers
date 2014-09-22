"""
 Title: test_tc2mz_orig.py 
 Author: Tina Yang, tina.yang@ga.gov.au 
 CreationDate: 2014-06-02
 Description: Unit testing module for tc2mz_orig function in terrain_mult.py 
 Version: $Rev$ 
 $Id$
"""

import unittest
import numpy as np
from numpy.testing import assert_almost_equal

import sys
import os.path
from inspect import getfile, currentframe


class TestTc2mz_orig(unittest.TestCase):

    def setUp(self):        
               
        self.data_spacing = 25       
    
           
    def test_tc2mz_orig(self): 
        
        cmd_folder = os.path.realpath(os.path.abspath(os.path.split(getfile(currentframe()))[0]))         
        
        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))
                
        if parent not in sys.path:
            sys.path.insert(0, parent)
            
        from terrain.terrain_mult import tc2mz_orig
        
        data = np.array([[2,4,4,5,13,11],
                      [7,14,3,1,8,6],
                      [1,9,4,7,2,8],
                      [2,5,15,12,7,8],
                      [3,8,3,1,5,2],
                      [2,9,4,15,1,3]])
    
        cycl = np.array([[1,0,0,0,0,0],
                          [0,0,0,1,0,0],
                          [0,0,0,0,0,0],
                          [0,0,0,0,0,0],
                          [0,0,0,1,0,0],
                          [0,0,0,0,1,0]])
                                                      
                 
        scripts_result = tc2mz_orig(cycl, data)
        
        np.set_printoptions(precision=3)
        
        expect_result = np.array([[0.873,0.806,0.806,0.83,1.063,1.063],
                                  [0.949,0.898,0.782,0.863,1,0.919],
                                  [0.750,1,0.806,0.949,0.774,1],
                                  [0.774,0.830,1.084,1,0.949,1],
                                  [0.782,1,0.782,0.863,0.830,0.774],
                                  [0.774,1,0.806,1.084,0.863,0.782]])
            
        
        assert_almost_equal(scripts_result, expect_result, decimal=2, err_msg='',verbose=True)  


if __name__ == "__main__":
    unittest.main()
