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


class TestTerrainMultiplier(unittest.TestCase):

    def setUp(self):
        
        # A single line of elevation data to use in the tests:        
        self.terrain_buffer = 1000.
        self.pixelwidth = 25.
        self.reclassified_array = np.empty([3, 640])
        self.reclassified_array[:,0:160] = 1.048
        self.reclassified_array[:,160:200] = 0.83
        self.reclassified_array[:,200:240] = 0.75
        self.reclassified_array[:,240:320] = 1.048
        self.reclassified_array[:,320:360] = 0.83
        self.reclassified_array[:,360:400] = 0.782
        self.reclassified_array[:,400:440] = 0.75
        self.reclassified_array[:,440:520] = 1.048
        self.reclassified_array[:,520:560] = 0.83
        self.reclassified_array[:,560:600] = 0.782
        self.reclassified_array[:,600:640] = 1.048
    
        
    def test_convo_w(self):
        
        def interp(start_x, end_x, start_y, end_y):
            
            interp_result = np.empty([3, end_x - start_x])
            xp = [start_x, end_x]
            fp = [start_y, end_y]
            for x in range(start_x, end_x):
                 interp_result[:, x-start_x] = np.interp(x, xp, fp)
                 
            return interp_result
        
        
        mz_engineered = np.empty([3, 640])
        mz_engineered[:,0:160] = 1.048
        mz_engineered[:,160:200] = interp(160, 200, 1.048, 0.83)
        mz_engineered[:,200:240] = interp(200, 240, 0.83, 0.75)
        mz_engineered[:,240:280] = interp(240, 280, 0.75, 1.048)
        mz_engineered[:,280:320] = 1.048
        mz_engineered[:,320:360] = interp(320, 360, 1.048, 0.83)
        mz_engineered[:,360:400] = interp(360, 400, 0.83, 0.782)
        mz_engineered[:,400:440] = interp(400, 440, 0.782, 0.75)
        mz_engineered[:,440:480] = interp(440, 480, 0.75, 1.048)
        mz_engineered[:,480:520] = 1.048
        mz_engineered[:,520:560] = interp(520, 560, 1.048, 0.83)
        mz_engineered[:,560:600] = interp(560, 600, 0.83, 0.782)
        mz_engineered[:,600:640] = interp(600, 640, 0.782, 1.048)
                
        
        cmd_folder = os.path.realpath(
                     os.path.abspath(os.path.split(
                     getfile(currentframe()))[0]))         
        
        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))
        
            
        if parent not in sys.path:
            sys.path.insert(0, parent) 
            
        from terrain.terrain_mult import convo_w
        
        filter_width = int(self.terrain_buffer / self.pixelwidth)
            
        outdata = convo_w(self.reclassified_array, filter_width)

        #plot the line profile
#        point_no = outdata.shape[1]
#        print point_no
#        x = np.arange(point_no)
#        y = outdata[1,:].flatten()
#        print y
#        pyplot.plot(x, y, 'g')
#        pyplot.show()

        mz_scripts = outdata[1,:]          
        
        assert_almost_equal(mz_scripts,  mz_engineered[1,:], decimal=2, err_msg='',verbose=True)
        #assert_allclose(mz_scripts, mz_engineered[1,:], rtol=0.01, atol=0, err_msg='',verbose=True)


if __name__ == "__main__":
    unittest.main()
