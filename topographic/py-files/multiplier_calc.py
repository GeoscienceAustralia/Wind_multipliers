##------------------------------------------------------
## Computes the multipliers for a data line
##------------------------------------------------------
import logging as log
import numpy as np
import Mh            # calculate Mh using the simpler formula modified by C.Thomas 2009        
from findpeaks import findpeaks, findvalleys     # get the indices of the ridges in a data line


def multiplier_calc(line, data_spacing):
# --------------------------------------------------------
# initialise M as an array filled with 1
# --------------------------------------------------------
  nrow = np.size(line)
  M = np.ones((nrow, 1), dtype=float)

  # take the largest integer of each element of the data line
  fwd_line = np.floor(line)

  # Get the indices of the ridges & valleys
  ridge_ind  = findpeaks(fwd_line)        # relative ind
  valley_ind = findvalleys(fwd_line)    # relative ind

  if np.size(ridge_ind) == 0: # the DEM is completely flat
     log.debug( "Flat line" )
     
  elif np.size(ridge_ind) == 1 and ridge_ind[0] == 0:  # the DEM is downward slope all the time
     log.debug( "Downward slope" )
    
  else:                        # 2 general cases, calculate m, works as Mh.m
             
      if ridge_ind[0] == 0:    # (1) down up down up ....
         for i in range(1, np.size(ridge_ind)):
            m = Mh.Mh(fwd_line, ridge_ind[i], valley_ind[i-1], data_spacing)
            M = np.maximum(M, m)
      
      else:                    # (2) up dowm up dowm ....
         for i in range(0, np.size(ridge_ind)):
            m = Mh.Mh(fwd_line, ridge_ind[i], valley_ind[i], data_spacing)
            M = np.maximum(M, m)

  return M
