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
#from matplotlib import pyplot
from inspect import getfile, currentframe

#import terrain.terrain_mult as convo_w


class TestTerrainMultiplier(unittest.TestCase):

#    def setUp(self):
#        
#        # A single line of elevation data to use in the tests:        
#        self.terrain_buffer = 1000.
#        self.pixelwidth = 25.
#        self.reclassified_array = np.empty([3, 640])
#        self.reclassified_array[:,0:160] = 1.048
#        self.reclassified_array[:,160:200] = 0.83
#        self.reclassified_array[:,200:240] = 0.75
#        self.reclassified_array[:,240:320] = 1.048
#        self.reclassified_array[:,320:360] = 0.83
#        self.reclassified_array[:,360:400] = 0.782
#        self.reclassified_array[:,400:440] = 0.75
#        self.reclassified_array[:,440:520] = 1.048
#        self.reclassified_array[:,520:560] = 0.83
#        self.reclassified_array[:,560:600] = 0.782
#        self.reclassified_array[:,600:640] = 1.048
    
        
#    def test_convo_w(self):
#        
#        def interp(start_x, end_x, start_y, end_y):
#            
#            interp_result = np.empty([3, end_x - start_x])
#            xp = [start_x, end_x]
#            fp = [start_y, end_y]
#            for x in range(start_x, end_x):
#                 interp_result[:, x-start_x] = np.interp(x, xp, fp)
#                 
#            return interp_result
#        
#        
#        mz_engineered = np.empty([3, 640])
#        mz_engineered[:,0:160] = 1.048
#        mz_engineered[:,160:200] = interp(160, 200, 1.048, 0.83)
#        mz_engineered[:,200:240] = interp(200, 240, 0.83, 0.75)
#        mz_engineered[:,240:280] = interp(240, 280, 0.75, 1.048)
#        mz_engineered[:,280:320] = 1.048
#        mz_engineered[:,320:360] = interp(320, 360, 1.048, 0.83)
#        mz_engineered[:,360:400] = interp(360, 400, 0.83, 0.782)
#        mz_engineered[:,400:440] = interp(400, 440, 0.782, 0.75)
#        mz_engineered[:,440:480] = interp(440, 480, 0.75, 1.048)
#        mz_engineered[:,480:520] = 1.048
#        mz_engineered[:,520:560] = interp(520, 560, 1.048, 0.83)
#        mz_engineered[:,560:600] = interp(560, 600, 0.83, 0.782)
#        mz_engineered[:,600:640] = interp(600, 640, 0.782, 1.048)
#                
#        
#        cmd_folder = os.path.realpath(
#                     os.path.abspath(os.path.split(
#                     getfile(currentframe()))[0]))         
#        
#        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))
#        
#            
#        if parent not in sys.path:
#            sys.path.insert(0, parent) 
#            
#        from terrain.terrain_mult import convo_w
#        
#        filter_width = int(self.terrain_buffer / self.pixelwidth)
#            
#        outdata = convo_w(self.reclassified_array, filter_width)
#
#        #plot the line profile
##        point_no = outdata.shape[1]
##        print point_no
##        x = np.arange(point_no)
##        y = outdata[1,:].flatten()
##        print y
##        pyplot.plot(x, y, 'g')
##        pyplot.show()
#
#        mz_scripts = outdata[1,:] 
#
#        #print mz_scripts         
#        
#        assert_almost_equal(mz_scripts,  mz_engineered[1,:], decimal=2, err_msg='',verbose=True)
#        #assert_allclose(mz_scripts, mz_engineered[1,:], rtol=0.01, atol=0, err_msg='',verbose=True)
        
        

#    def test_convo_old(self):
#        
#        def interp(start_x, end_x, start_y, end_y):
#            
#            interp_result = np.empty([3, end_x - start_x])
#            xp = [start_x, end_x]
#            fp = [start_y, end_y]
#            for x in range(start_x, end_x):
#                 interp_result[:, x-start_x] = np.interp(x, xp, fp)
#                 
#            return interp_result
#        
#        
##        import pdb
##        pdb.set_trace()
#        
#        mz_engineered = np.empty([3, 640])
#        mz_engineered[:,0:160] = 1.048
#        mz_engineered[:,160:200] = interp(160, 200, 1.048, 0.83)
#        mz_engineered[:,200:240] = interp(200, 240, 0.83, 0.75)
#        mz_engineered[:,240:280] = interp(240, 280, 0.75, 1.048)
#        mz_engineered[:,280:320] = 1.048
#        mz_engineered[:,320:360] = interp(320, 360, 1.048, 0.83)
#        mz_engineered[:,360:400] = interp(360, 400, 0.83, 0.782)
#        mz_engineered[:,400:440] = interp(400, 440, 0.782, 0.75)
#        mz_engineered[:,440:480] = interp(440, 480, 0.75, 1.048)
#        mz_engineered[:,480:520] = 1.048
#        mz_engineered[:,520:560] = interp(520, 560, 1.048, 0.83)
#        mz_engineered[:,560:600] = interp(560, 600, 0.83, 0.782)
#        mz_engineered[:,600:640] = interp(600, 640, 0.782, 1.048)
#                
#        
#        cmd_folder = os.path.realpath(
#                     os.path.abspath(os.path.split(
#                     getfile(currentframe()))[0]))         
#        
#        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))
#        
#            
#        if parent not in sys.path:
#            sys.path.insert(0, parent) 
#            
#        from terrain.terrain_mult import convo
#        
#        filter_width = int(self.terrain_buffer / self.pixelwidth)
#            
#        outdata = convo('e', self.reclassified_array, filter_width)
#
#        #plot the line profile
##        point_no = outdata.shape[1]
##        print point_no
##        x = np.arange(point_no)
##        y = outdata[1,:].flatten()
##        print y
##        pyplot.plot(x, y, 'g')
##        pyplot.show()
#
#        mz_scripts = outdata[1,:]   
#        
#        print mz_scripts  
#        
#        assert_almost_equal(mz_scripts,  mz_engineered[1,:], decimal=2, err_msg='',verbose=True)
#        #assert_allclose(mz_scripts, mz_engineered[1,:], rtol=0.01, atol=0, err_msg='',verbose=True)


    def test_convo(self):        
        
#        import pdb
#        pdb.set_trace()
        
        Mz_exp_w =  np.array([[0., 1., 2., 0., 0.5, 1., 1.5, 2.5],
                             [ 8., 9., 10., 8., 8.5, 9., 9.5, 10.5],
                             [ 16., 17., 18., 16., 16.5, 17., 17.5, 18.5],
                             [ 24., 25., 26., 24., 24.5, 25., 25.5, 26.5],
                             [ 32.,33.,34.,32.,32.5,33.,33.5,34.5],
                             [ 40.,41.,42.,40.,40.5,41.,41.5,42.5],
                             [ 48.,49.,50.,48.,48.5,49.,49.5,50.5],
                             [ 56.,57.,58.,56.,56.5,57.,57.5,58.5]])
                             
                             
        Mz_exp_e =  np.array([[4.5,5.5,6.,6.5,7.,5.,6.,7.],
                             [ 12.5,13.5,14.,14.5,15.,13.,14.,15.],
                             [ 20.5,21.5,22.,22.5,23.,21.,22.,23.],
                             [ 28.5,29.5,30.,30.5,31.,29.,30.,31.],
                             [ 36.5,37.5,38.,38.5,39.,37.,38.,39.],
                             [ 44.5,45.5,46.,46.5,47.,45.,46.,47.],
                             [ 52.5,53.5,54.,54.5,55.,53.,54.,55. ],
                             [ 60.5,61.5,62.,62.5,63.,61.,62.,63. ]])
                             
                             
        Mz_exp_n =  np.array([[  0., 1., 2., 3., 4., 5., 6., 7.],
                             [  8., 9., 10., 11., 12., 13., 14., 15.],
                             [ 16., 17., 18., 19., 20., 21., 22., 23.],
                             [  0., 1.,2.,3.,4.,5.,6.,7.],
                             [  4.,5.,6.,7.,8.,9.,10.,11.],
                             [  8.,9.,10.,11.,12.,13.,14.,15.],
                             [ 12.,13.,14.,15.,16.,17.,18.,19.],
                             [ 20.,21.,22.,23.,24.,25.,26.,27.]])
        
                
        Mz_exp_s =  np.array([[ 36.,  37.,  38.,  39.,  40.,  41.,  42.,  43.],
                             [  44.,  45.,  46.,  47.,  48.,  49.,  50.,  51.],
                             [  48.,  49.,  50.,  51.,  52.,  53.,  54.,  55.],
                             [  52.,  53.,  54.,  55.,  56.,  57.,  58.,  59.],
                             [  56.,  57.,  58.,  59.,  60.,  61.,  62.,  63.],
                             [  40.,  41.,  42.,  43.,  44.,  45.,  46.,  47.],
                             [  48.,  49.,  50.,  51.,  52.,  53.,  54.,  55.],
                             [  56.,  57.,  58.,  59.,  60.,  61.,  62.,  63. ]])
                             
                             
        Mz_exp_nw =  np.array([[ 0.,    1.,    2.,   3.,    4.,    5.,    6.,    7. ],
                             [  8.,    9.,   10.,   11.,   12.,   13.,   14.,   15.],
                             [  16.,   17.,   18.,   19.,   20.,   21.,   22.,   23.],
                             [  24.,   25.,   26.,    0.,    1.,    2.,    3.,    4. ],
                             [  32.,   33.,   34.,    8.,    4.5,   5.5,   6.5,   7.5],
                             [  40.,   41.,   42.,   16.,   12.5,   9.,   10.,   11.],
                             [  48.,   49.,   50.,   24.,   20.5,  17.,   13.5,  14.5],
                             [  56.,   57.,   58.,   32.,   28.5,  25.,   21.5,  22.5 ]])
                             
                             
        Mz_exp_ne =  np.array([[ 0.,    1.,    2.,   3.,    4.,    5.,    6.,    7. ],
                             [  8.,    9.,   10.,   11.,   12.,   13.,   14.,   15.],
                             [  16.,   17.,   18.,   19.,   20.,   21.,   22.,   23.],
                             [  3.,    4.,    5.,    6.,    7.,   29.,   30.,   31. ],
                             [  7.5,   8.5,   9.5,  10.5,  15.,   37.,   38.,   39.],
                             [  12.,   13.,   14.,   18.5,  23.,   45.,   46.,   47.],
                             [  16.5,  17.5,  22.,   26.5,  31.,   53.,   54.,   55. ],
                             [  24.5,  25.5,  30.,   34.5,  39.,   61.,   62.,   63. ]])
                             
                             
        Mz_exp_se =  np.array([[40.5,  41.5,  38.,   34.5,  31.,    5.,    6.,    7., ],
                             [  48.5,  49.5,  46.,   42.5,  39.,   13.,   14.,   15.,],
                             [  52.,   53.,   54.,   50.5,  47.,   21.,   22.,   23.],
                             [  55.5,  56.5,  57.5,  58.5,  55.,   29.,   30.,   31.,],
                             [  59.,   60.,   61.,   62.,   63.,   37.,   38.,   39.],
                             [  40.,   41.,   42.,   43.,   44.,   45.,   46.,   47. ],
                             [  48.,   49.,   50.,   51.,   52.,   53.,   54.,   55. ],
                             [  56.,   57.,   58.,   59.,   60.,   61.,   62.,   63. ]])
                             
                             
        Mz_exp_sw =  np.array([[0.,    1.,    2.,   24.,   28.5,  33.,   37.5,  38.5 ],
                             [  8.,    9.,   10.,   32.,   36.5,  41.,   45.5,  46.5,],
                             [  16.,   17.,   18.,   40.,   44.5,  49.,   50.,   51.],
                             [  24.,   25.,   26.,   48.,   52.5,  53.5,  54.5,  55.5],
                             [  32.,   33.,   34.,   56.,   57.,   58.,   59.,   60.],
                             [  40.,   41.,   42.,   43.,   44.,   45.,   46.,   47. ],
                             [  48.,   49.,   50.,   51.,   52.,   53.,   54.,   55. ],
                             [  56.,   57.,   58.,   59.,   60.,   61.,   62.,   63. ]])
        
        
        cmd_folder = os.path.realpath(
                     os.path.abspath(os.path.split(
                     getfile(currentframe()))[0]))         
        
        parent = os.path.abspath(os.path.join(cmd_folder, os.pardir))
        
            
        if parent not in sys.path:
            sys.path.insert(0, parent) 
            
        from terrain.terrain_mult import convo
        
                
        data = np.arange(64).reshape(8, 8)  
        avg_width = 4
        lag_width = 2
                
        #dire = ['w', 'e', 'n', 's', 'nw', 'ne', 'se', 'sw']
        dire = ['sw']
        
        for one_dir in dire:

            outdata = convo(one_dir, data, avg_width, lag_width)
            
            print one_dir
        
            print data
            print outdata
            
#            Mz_exp = '%s' % 'Mz_' + one_dir + '_exp'
#            
#            print Mz_exp
#        
            assert_almost_equal(outdata,  Mz_exp_sw, decimal=2, err_msg='',verbose=True)


if __name__ == "__main__":
    unittest.main()
