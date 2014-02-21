##------------------------------------------------------
##  Multiplier calculations
##------------------------------------------------------

import numpy as np


def escarpment_factor(profile, ridge, valley, data_spacing):
    """
    Calculate escarpment factor
    """
    max_escarp = 3
    min_escarp = 0.5
    nrow = np.size(profile)

    H  = profile[ridge] - profile[valley]
    Lu = abs(ridge - valley) * data_spacing / 2
    slope = H / (2 * Lu)
    beta_ind = np.minimum(nrow - 1, np.floor(ridge + (2 * Lu / data_spacing)))
    H_r2beta = profile[ridge] - profile[beta_ind]
    D_r2beta = (beta_ind - ridge) * data_spacing
    if D_r2beta > 0:                 # D_r2beta can be 0, 25, 50, ...
        slope_r2mL2 = H_r2beta/D_r2beta
        
        # when a symmetrical ridge slope_r2mL2=slope so escarp_factor=1
        # If slope_r2mL2=0, escarp_factor=2.5
        escarp_factor = 2.5 - 1.5 * slope_r2mL2 / slope   
                                                     
        if escarp_factor < min_escarp:               
            escarp_factor = min_escarp
        elif escarp_factor > max_escarp:
            escarp_factor = max_escarp
        
    else:      # the ridge is on the end
        slope_r2mL2 = 999
        escarp_factor = 1
    return escarp_factor

def Mh(profile, ridge, valley, data_spacing):
# --------------------------------------------------------
# initialise parameters
# --------------------------------------------------------

    H_threshold = 10     # height threshold for Mh calculation
    Lu_threshold = data_spacing    # half distance threshold for Mh calculation
    
    Z = 0            #building height
    nrow = np.size(profile)
    m = np.ones((nrow, 1), dtype=float)
    
    H  = profile[ridge] - profile[valley]
    Lu = abs(ridge - valley) * data_spacing / 2
    slope = H / (2 * Lu)
    L1 = np.maximum(0.36 * Lu, 0.4 * H)
    L2 = 4 * L1 
    
    escarp_factor = escarpment_factor(profile, ridge, valley, data_spacing)
    fL2_ind = np.maximum(0, ridge - np.floor(L2 / data_spacing))
    if slope < 0.05 or H < H_threshold or Lu < Lu_threshold:
        return m
    
    # calculate the Mh from the front L2 to the back L2 with the escarpment
    # factor considered:
    l1 = int(np.floor(fL2_ind)) - 1
    l2 = int(np.floor(np.minimum(nrow - 1, ridge + \
                np.floor(escarp_factor * L2 / data_spacing)) + 1))

    for k in range(l1, l2): 
        x  = (ridge - k) * data_spacing
        
        # within the region of L2 up to the ridge
        if x >= 0 and x < L2:        
            m[k] = 1 + (H / (3.5 * (Z + L1))) * (1 - abs(x) / L2)
            # --------------------------------------------------------
            # for larger slopes, you still use the formula to calculate M,
            # then re-value to 1.71 when it islarger. If use 1.71 for any slope 
            # greater than 0.45, then all the points within the L2 zone will 
            # have 1.71 rather than a gradual increaing, peaks and decreasing 
            # pattern.
            # --------------------------------------------------------
            if m[k] > 1.71:
                m[k] = 1.71
                
        # more or less a symmetrical hill
        elif ( (slope > 0.45) and (x < 0) and (x > -H/4) and \
            (abs(escarp_factor - 1) < 0.2) ): 
            m[k] = 1 + 0.71 * (1 - abs(x) / (escarp_factor * L2))
            
        # within the region from the ridge2 up to the back L2
        elif x < 0 and x > -escarp_factor*L2:  
            m[k] = 1 + (H / (3.5 * (Z + L1))) * (1 - abs(x) / \
            (escarp_factor * L2))   
            if m[k] > 1.71:
                m[k] = 1.71

    return m  
    
    
