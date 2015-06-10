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

import sys
import os.path
import unittest
import numpy as np
from numpy.testing import assert_allclose, assert_almost_equal
from inspect import getfile, currentframe


class TestShieldingMultiplier(unittest.TestCase):

    def setUp(self):
        
        # A single line of elevation data to use in the tests:
        self.pixelwidth = 25.
        self.ms_orig = np.ones([3, 640])
        self.ms_orig[:,160:200] = 0.85
        self.ms_orig[:,200:240] = 0.9
        self.ms_orig[:,320:360] = 0.85
        self.ms_orig[:,360:400] = 0.88
        self.ms_orig[:,400:440] = 0.9
        self.ms_orig[:,520:560] = 0.85
        self.ms_orig[:,560:600] = 0.88
        
        self.slope_array = np.zeros([3, 640])        
        self.slope_array[:,320:360] = 3.44
        self.slope_array[:,360:400] = 3.44
        self.slope_array[:,520:560] = 12.68
        self.slope_array[:,560:600] = 12.68        
        
        self.aspect_array = np.empty([3, 640])
        self.aspect_array.fill(9)         
        self.aspect_array[:,320:360] = 7
        self.aspect_array[:,360:400] = 3
        self.aspect_array[:,520:560] = 7
        self.aspect_array[:,560:600] = 3
        
    def test_combine(self):

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
        ms_engineered[321] = 0.957
        ms_engineered[322] = 0.839
        ms_engineered[323:360] = 0.768
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
        
                
        cmd_folder = os.path.realpath(
                     os.path.abspath(os.path.split(
                     getfile(currentframe()))[0]))         
        
        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))
            
        if parent not in sys.path:
            sys.path.insert(0, parent) 
            
        from shielding.shield_mult import kern_w, blur_image, combine        
        
        kernel_size = int(100.0 / self.pixelwidth) - 1

        if kernel_size > 0:
            outdata = np.zeros_like(self.ms_orig, dtype=np.float32)
            mask = kern_w(kernel_size)
            outdata = blur_image(self.ms_orig, mask)
        else:
            outdata = self.ms_orig

            
        result = combine(outdata, self.slope_array, self.aspect_array, 'w')

        # get the computed mz from scripts using the test line total
        mh_scripts = result[1,:].flatten() 
        np.set_printoptions(precision=3)
        
        assert_almost_equal(mh_scripts, ms_engineered, decimal=2, err_msg='',verbose=True)


    def test_init_kern(self):
        
        cmd_folder = os.path.realpath(
                     os.path.abspath(os.path.split(
                     getfile(currentframe()))[0]))         
        
        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))
        
        if parent not in sys.path:
            sys.path.insert(0, parent) 
            
        from shielding.shield_mult import init_kern, init_kern_diag    


        init_kernel_expect = np.array([[ 0.,    0.,    0.,    0.,    0.  ],
                                [ 0.,    0.,    0.,    0.,    0.  ],
                                [ 0.,    0.,    0.,    0.,    0.  ],
                                [ 0.,    0.,    0.25,  0.,    0.  ],
                                [ 0.,    0.25,  0.25,  0.25,  0.  ]])         
        
        init_kernel_diag_expect = np.array([[ 0.,  0.,  0.,  0.33,  0.],
                                             [ 0.,  0.,  0.,  0.33,  0.33],
                                             [ 0.,  0.,  0.,  0.,  0.],
                                             [ 0.,  0.,  0.,  0.,  0.],
                                             [ 0.,  0.,  0.,  0.,  0.]])    
        
        
        kernel_size = 2
        
        
        init_kernel = init_kern(kernel_size)
        init_kernel_diag = init_kern_diag(kernel_size)
        
        assert_almost_equal(init_kernel, init_kernel_expect, decimal=2, err_msg='',verbose=True)
        assert_almost_equal(init_kernel_diag, init_kernel_diag_expect, decimal=2, err_msg='',verbose=True)
        


if __name__ == "__main__":
    unittest.main()
