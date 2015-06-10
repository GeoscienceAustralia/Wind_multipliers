"""
    Title: test_tasmania.py 
    Author: Tina Yang, tina.yang@ga.gov.au 
    CreationDate: 2014-05-01
    Description: Unit testing module for tasmania function in 
                 topomult.py 
    Version: $Rev$ 
    $Id$
"""

import sys
import os.path
import unittest
import numpy as np
from numpy.testing import assert_allclose
from inspect import getfile, currentframe


class TestTasmania(unittest.TestCase):       
        
    def test_tasmania(self):
        cmd_folder = os.path.realpath(os.path.abspath(os.path.split(getfile(currentframe()))[0]))         
        
        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))
        
        grandparent = os.path.abspath(os.path.join(parent, os.pardir))
                
        if grandparent not in sys.path:
            sys.path.insert(0, grandparent) 
            
        from topographic.topomult import tasmania
        
        mh_tas_expect = np.array([[ 1.0, 1.1, 1.2, 1.39945, 1.5092, 1.61925, 1.7296, 1.84025],
                                  [ 0.9, 1., 1.1, 1.2, 1.39945, 1.5092, 1.61925, 1.7296 ],
                                  [ 0.8, 0.9, 1., 1.1, 1.2, 1.39945, 1.5092, 1.61925],
                                  [ 0.7, 0.8, 0.9, 1., 1.1, 1.2, 1.39945, 1.5092 ],
                                  [ 0.6, 0.7, 0.8, 0.9, 1., 1.1, 1.2, 1.39945],
                                  [ 0.5, 0.6, 0.7, 0.8, 0.9, 1., 1.1, 1.2],
                                  [ 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1., 1.18415],
                                  [ 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.96885,1.078]])
        
       
        mhdata = np.array([[1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7],
                           [0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6],
                           [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5],
                           [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4],
                           [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3],
                           [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2],
                           [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1],
                           [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]])
                           
        dem = np.array([[480, 490, 500, 510, 520, 530, 540, 550],
                        [470, 480, 490, 500, 510, 520, 530, 540],
                        [460, 470, 480, 490, 500, 510, 520, 530],
                        [450, 460, 470, 480, 490, 500, 510, 520],
                        [440, 450, 460, 470, 480, 490, 500, 510],
                        [430, 440, 450, 460, 470, 480, 490, 500],
                        [440, 450, 460, 470, 480, 490, 500, 510],
                        [450, 460, 470, 480, 490, 500, 510, 520]])                   
        
        mh_tas_scripts = tasmania(mhdata, dem)
        
        #print mh_tas_scripts
       
           
        #assert_almost_equal(mh_engineered_total, mh_scripts_selection_total, decimal=2, err_msg='',verbose=True)
        assert_allclose(mh_tas_scripts, mh_tas_expect, rtol=0.04, atol=0, err_msg='',verbose=True)


if __name__ == "__main__":
    unittest.main()
