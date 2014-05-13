##------------------------------------------------------
## Computes the multipliers for a data line
##------------------------------------------------------
import numpy
import Mh            # calculate Mh using the simpler formula modified by C.Thomas 2009        
import findpeaks     # get the indices of the ridges in a data line
import findvalleys   # get the indices of the valleys in a data line 

def multiplier_calc(line, data_spacing):
# --------------------------------------------------------
# initialise M as an array filled with 1
# --------------------------------------------------------
  nrow = numpy.size(line)
  M = numpy.ones((nrow,1),dtype=float)

  # take the largest integer of each element of the data line
  fwd_line = numpy.floor(line)

  # Get the indices of the ridges & valleys
  ridge_ind  = findpeaks.findpeaks(fwd_line)        # relative ind
  valley_ind = findvalleys.findvalleys(fwd_line)    # relative ind
 
  if numpy.size(ridge_ind) == 0: # the DEM is completely flat
     print "Flat line"
     
  elif numpy.size(ridge_ind) == 1 and ridge_ind[0] == 0:  # the DEM is downward slope all the time
     print "Downward slope"
    
  else:                        # 2 general cases, calculate m, works as Mh.m
             
      if ridge_ind[0] == 0:    # (1) down up down up ....
         for i in range(1,numpy.size(ridge_ind)):
            m = Mh.Mh(fwd_line,ridge_ind[i],valley_ind[i-1],data_spacing)
            M = numpy.maximum(M, m)
      
      else:                    # (2) up dowm up dowm ....
         for i in range(0,numpy.size(ridge_ind)):
            m = Mh.Mh(fwd_line,ridge_ind[i],valley_ind[i],data_spacing)
            M = numpy.maximum(M, m)

  return M
