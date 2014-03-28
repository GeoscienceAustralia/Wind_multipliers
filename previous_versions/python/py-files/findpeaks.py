## --------------------------------------------------------
## Generate the indices of the ridges in a data line
## --------------------------------------------------------

import numpy

def findpeaks(y):
  
    dy = numpy.diff(y)
    if y.size == 0:
        ind = []
        return ind
    
    if y.size == 1:
        ind = [0]
        return ind
      
    dy_z = numpy.array(numpy.where(dy==0))
    if dy.size == dy_z.size:
        ind = []
        return ind

    dy_a1 = numpy.append(dy,[0])
    dy_a2 = numpy.append([1],dy)
    
    ind_a1 = numpy.array((dy_a1<=0).nonzero())
    ind_a2 = numpy.array((dy_a2>0).nonzero())
    
    ind = numpy.intersect1d(ind_a1,ind_a2)
    
    if ind[0] == 0:
        if dy[0] == 0:         # There is a plateau at the start
            non_zero_ind = (dy != 0).nonzero()
           
            if dy[non_zero_ind[0][0]] > 0:
                # The plateau at the start is a valley, so remove it from the list
                ind = ind[1:]
    
    if ind[-1] == numpy.size(y):
        if dy[-1] == 0:         # There is a plateau at the end
            non_zero_ind = (dy != 0).nonzero()
            if dy[non_zero_ind[0][-1]] < 0: 
               ind = ind[0:-2]   # The plateau at the end is a valley, so remove it from the list

    # Get the values that are at the start of plateaus, or are peaks
    
    ind_v = numpy.append([0],numpy.diff(ind))
    ind = numpy.compress(ind_v!=1, ind)   

    return ind