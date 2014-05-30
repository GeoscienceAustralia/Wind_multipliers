import unittest
import numpy as np
from numpy.testing import assert_almost_equal
from matplotlib import pyplot
import logging as log
from topographic.findpeaks import findpeaks, findvalleys
from test_all_topo_engineered_data import test_line, expect_results
from topographic.Mh import escarpment_factor as escarpment_factor

class TestFindpeaks(unittest.TestCase):

    def setUp(self):        
               
        self.data_spacing = 25       

    def test_findpeaks(self): 
        
#        import pdb
#        pdb.set_trace()
               
        # test for each scenerio               
        for p in range(3, len(test_line)+1):
        #for p in range(3, 4):
            print '\ntest ' + str(p) + ' ...'  
            nrow = np.size(test_line[p])
            
            # take the largest integer of each element of the data line
            fwd_line = np.floor(test_line[p])
           
            
            # Get the indices of the ridges & valleys
            ridge_ind  = findpeaks(fwd_line)        # relative ind
            valley_ind = findvalleys(fwd_line)    # relative ind
            
            print ridge_ind
            print valley_ind            
            
            nrow = np.size(ridge_ind)
            H = np.ones((nrow, 1), dtype=float)
            slope = np.ones((nrow, 1), dtype=float)
            downwind_slope = np.ones((nrow, 1), dtype=float)
            escarp_factor = np.ones((nrow, 1), dtype=float)
            
            if np.size(ridge_ind) == 0: # the DEM is completely flat
               log.debug( "Flat line" )
                 
            elif np.size(ridge_ind) == 1 and ridge_ind[0] == 0:  # the DEM is downward slope all the time
               log.debug( "Downward slope" )
                
            else:                        # 2 general cases, calculate m, works as Mh.m
                         
                if ridge_ind[0] == 0:    # (1) down up down up ....
                    for i in range(1, np.size(ridge_ind)):
                        H[i], slope[i], downwind_slope[i], escarp_factor[i] = escarpment_factor(fwd_line, ridge_ind[i], valley_ind[i-1], self.data_spacing)                      
                  
                else:                    # (2) up dowm up dowm ....
                    for i in range(0, np.size(ridge_ind)):
                        H[i], slope[i], downwind_slope[i], escarp_factor[i] = escarpment_factor(fwd_line, ridge_ind[i], valley_ind[i], self.data_spacing)
        
            hill_no = np.size(ridge_ind) 
            
            scripts_result = np.concatenate([[hill_no], H.flatten(), slope.flatten(), downwind_slope.flatten(), escarp_factor.flatten()])
            #scripts_result = [[hill_no], H.flatten(), slope.flatten(), downwind_slope.flatten(), escarp_factor.flatten()]            
            
            print scripts_result
            print expect_results[p]
                  
        
            #plot the line profile
#            point_no = len(test_line[p])
#            x = np.arange(point_no)
#            y = test_line[p]
#            pyplot.plot(x, y, 'g')
#            pyplot.show()

            
            assert_almost_equal(scripts_result, expect_results[i], decimal=2, err_msg='',verbose=True)  


if __name__ == "__main__":
    unittest.main()
