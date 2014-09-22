"""
 Title: test_combine.py 
 Author: Tina Yang, tina.yang@ga.gov.au 
 CreationDate: 2014-06-02
 Description: Unit testing module for combine function in shield_mult.py 
 Version: $Rev$ 
 $Id$
"""

import unittest
import numpy as np
from numpy.testing import assert_almost_equal

import sys
import os.path
from inspect import getfile, currentframe


class TestCombine(unittest.TestCase):

    def setUp(self):        
               
        self.data_spacing = 25       
    
           
    def test_combine(self): 
        cmd_folder = os.path.realpath(os.path.abspath(os.path.split(getfile(currentframe()))[0]))         
        
        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))
                
        if parent not in sys.path:
            sys.path.insert(0, parent)
            
        from shielding.shield_mult import combine
        
        slope_array = np.array([[0.2,0.4,4,5,13,11],
                                  [7,14,3,1,8,6],
                                  [1.8,9,4,7,2,18],
                                  [2,5,15,12,7,8],
                                  [3.6,8,3,1,5,2],
                                  [2.8,9.6,4,15,1,3]])
        
        aspect_array = np.array([[1,2,3,4,5,5],
                                  [7,5,3,1,8,6],
                                  [7,7,4,7,2,7],
                                  [2,5,7,7,7,8],
                                  [7,8,3,1,5,2],
                                  [7,7,4,7,1,3]])
        
        ms_orig_array = np.array([[0.18,0.36,0.36,0.45,0.98,0.85],
                                  [0.74,0.94,0.27,0.09,0.82,0.92],
                                  [0.78,0.93,0.36,0.77,0.23,0.98],
                                  [0.22,0.58,0.85,0.28,0.77,0.83],
                                  [0.65,0.84,0.92,0.89,0.75,0.82],
                                  [0.89,0.96,0.45,0.85,0.93,0.38]])       
               
        one_dir = 'w'
        
        scripts_result = combine(ms_orig_array, slope_array, aspect_array, one_dir)
        
        np.set_printoptions(precision=2)
        
        expect_result = np.array([[0.16,0.32,0.32,0.41,0.96,0.77],
                                  [0.76,0.88,0.24,0.08,0.74,0.85],
                                  [0.70,0.95,0.32,0.78,0.21,1],
                                  [0.20,0.52,1,0.95,0.78,0.75],
                                  [0.60,0.76,0.85,0.80,0.68,0.74],
                                  [0.80,0.98,0.41,1,0.86,0.34]])
            
        
        assert_almost_equal(scripts_result, expect_result, decimal=2, err_msg='',verbose=True)  


if __name__ == "__main__":
    unittest.main()
