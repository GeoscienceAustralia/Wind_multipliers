# --------------------------------------------------------
# Returns a vector of array indices for a path
# starting at index n in a matrix of size nr by nc
# and proceeding in direction dir, where dir is one of 
# the 8 cardinal directions (n,s,e,w,ne,nw,se,sw). 
# Note that the array indices
# are all 1-d indices.
#
# thomas - mar 2009
# --------------------------------------------------------
import numpy

def make_path(nr,nc,n,dir):

      dir = dir.lower()
      #first compute the i,j coordinates from the 1-d index n
      i = numpy.mod(n,nr) + 1
      j = (n+1 - i)/nr + 1

      # find the i and j increments according to 
      # the directions in which we traverse
      
      if dir.find('n')>=0:
         i_incr = 1
      elif dir.find('s')>=0:
         i_incr = -1
      else:
        i_incr = 0
           
      if dir.find('w')>=0:
         j_incr = 1
      elif dir.find('e')>=0:
         j_incr = -1
      else:
         j_incr = 0
     
      # traverse, putting the positions in 1-index form
      result = []
      while ((i <= nr and i >= 1) and (j <= nc and j >= 1)):
             l = i+(j-1)*nr-1
             result.append(l)
             i += i_incr
             j += j_incr
      
      return result