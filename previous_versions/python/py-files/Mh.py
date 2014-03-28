##------------------------------------------------------
##  Multiplier calculations
##------------------------------------------------------

import numpy

def Mh(profile,ridge,valley,data_spacing):
# --------------------------------------------------------
# initialise parameters
# --------------------------------------------------------
     max_escarp = 3
     min_escarp = 0.5
     H_threshold = 10     # a hight (bwt ridge and valley) threshold for Mh calculation
     Lu_threshold = data_spacing     # a half distance (bwt ridge and valley) threshold for Mh calculation
    
     Z = 0            #building height
     dec_1pts = 1
     dec_2pts = 2
    
     nrow = numpy.size(profile)
     m = numpy.ones((nrow,1),dtype=float)
     min_h = profile.min(0)
     max_h = profile.max(0)
     H  = profile[ridge] - profile[valley]
     Lu = abs(ridge - valley) * data_spacing/2
     slope = H/(2*Lu)
                    
     L1 = numpy.maximum(0.36*Lu,0.4*H)
     L2 = 4*L1 
                    
    # fL2_ind - an absolute ind for the location of the front (face wind) L2
     fL2_ind = numpy.maximum(0, ridge - numpy.floor(L2/data_spacing)) # if fL2_ind goes before the start of DEM, chose 0

    # calculate the escarpment factor using the slope from -L2 position looks to the ridge
     beta_ind = numpy.minimum(nrow-1,numpy.floor(ridge+(2*Lu/data_spacing)))    # absolute ind with max nrow
     
     H_r2beta = profile[ridge] - profile[beta_ind] 
     # H_r2beta can be > = < 0
     D_r2beta = (beta_ind - ridge)*data_spacing    # D_r2beta is equal 2*Lu if nrow is reached
     if D_r2beta > 0:                 # D_r2beta can be 0, 25, 50, ...
        slope_r2mL2 = H_r2beta/D_r2beta
        escarp_factor = 2.5 - 1.5*slope_r2mL2/slope  # when a symatrical ridge slope_r2mL2=slope so escarp_factor=1 
                                                     # If slope_r2mL2=0, escarp_factor=2.5
        if escarp_factor < min_escarp:               # let us limit the factor to be at min_escarp
            escarp_factor = min_escarp
        elif escarp_factor > max_escarp:
            escarp_factor = max_escarp               # let us limit the factor to be at most max_escarp
        
     else:      # the ridge is on the end
        slope_r2mL2 = 999
        escarp_factor = 1
    
     if slope < 0.05 or H < H_threshold or Lu < Lu_threshold:
        return m
    
    #calculate the Mh from the front L2 to the back L2 with the escarpment factor considered
     l1 = int(numpy.floor(fL2_ind))-1
     l2 = int(numpy.floor(numpy.minimum(nrow-1, ridge + numpy.floor(escarp_factor*L2/data_spacing))+1))

     for k in range(l1, l2): 
         x  = (ridge - k) * data_spacing
         if x >= 0 and x < L2:        # within the region of L2 up to the ridge
              m[k] = 1 + (H/(3.5*(Z+L1))) * (1 - abs(x)/L2)
              # --------------------------------------------------------
              # for larger slopes, you still use the formula to calculate M, then re-value to 1.71 when it is
              # larger. If use 1.71 for any slope greater than 0.45, then all the points within the L2 zone will
              # have 1.71 rather than a gradual increaing, peaks and decreasing pattern.
              # --------------------------------------------------------
              if m[k] > 1.71:
                  m[k] = 1.71
              
         elif slope > 0.45 and x < 0 and x > -H/4 and abs(escarp_factor - 1) < 0.2: # more or less a symetrical hill
              m[k] = 1 + 0.71 * (1 - abs(x)/(escarp_factor*L2))
         elif x < 0 and x > -escarp_factor*L2:  # within the region from the ridge2 up to the back L2
              m[k] = 1 + (H/(3.5*(Z+L1))) * (1 - abs(x)/(escarp_factor*L2))   
              if m[k] > 1.71:
                 m[k] = 1.71

     return m  
    
    
