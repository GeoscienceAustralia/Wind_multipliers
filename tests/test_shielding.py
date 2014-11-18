"""
    Title: testmultipliercalc.py 
    Author: Tina Yang, tina.yang@ga.gov.au 
    CreationDate: 2014-05-01
    Description: Unit testing module for multiplier_cal function in 
                 multiplier_calc.py 
    Version: $Rev$ 
    $Id$
"""

import sys
import os.path
import unittest
import numpy as np
from numpy.testing import assert_allclose, assert_almost_equal
from matplotlib import pyplot
from inspect import getfile, currentframe

#import terrain.terrain_mult as convo_w


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
        
#        import pdb
#        pdb.set_trace()

        ms_engineered = np.ones(640)
        ms_engineered[160] = 0.963
        ms_engineered[161] = 0.926
        ms_engineered[162] = 0.821
        ms_engineered[163:200] = 0.765
        ms_engineered[200] = 0.771
        ms_engineered[201] = 0.776
        ms_engineered[202] = 0.793
        ms_engineered[203:240] = 0.810
        ms_engineered[240] = 0.833
        ms_engineered[241] = 0.856
        ms_engineered[242] = 0.926
        ms_engineered[243:320] = 1.0
        ms_engineered[320] = 0.963
        ms_engineered[321] = 0.926
        ms_engineered[322] = 0.821
        ms_engineered[323:340] = 0.765
        ms_engineered[340:360] = 0.769
        ms_engineered[360] = 0.768
        ms_engineered[361] = 0.772
        ms_engineered[362] = 0.782
        ms_engineered[363:400] = 0.792
        ms_engineered[400] = 0.794
        ms_engineered[401] = 0.797
        ms_engineered[402] = 0.803
        ms_engineered[403:440] = 0.810
        ms_engineered[440] = 0.833
        ms_engineered[441] = 0.856
        ms_engineered[442] = 0.926
        ms_engineered[443:520] = 1.0
#        ms_engineered[520] = 0.963
#        ms_engineered[521] = 0.926
#        ms_engineered[522] = 0.821
#        ms_engineered[523:528] = 0.765
#        ms_engineered[528:532] = 0.794
#        ms_engineered[532:536] = 0.851
#        ms_engineered[536:540] = 0.929
#        ms_engineered[540:560] = 1.000
        ms_engineered[560] = 0.768
        ms_engineered[561] = 0.772
        ms_engineered[562] = 0.782
        ms_engineered[563:600] = 0.792
        ms_engineered[600] = 0.806
        ms_engineered[601] = 0.828
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

        #plot the line profile
#        point_no = result.shape[1]
#        print point_no
#        x = np.arange(point_no)
#        y = result[1,:].flatten()
#        print y
#        pyplot.plot(x, y, 'g')
#        pyplot.show()

        # get the computed mz from scripts using the test line total
        mh_scripts = result[1,:].flatten()        
        
        assert_almost_equal(mh_scripts, ms_engineered, decimal=2, err_msg='',verbose=True)
        #assert_allclose(mh_scripts, ms_engineered, rtol=0.005, atol=0, err_msg='',verbose=True)


if __name__ == "__main__":
    unittest.main()
