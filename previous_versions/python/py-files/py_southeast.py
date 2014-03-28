##------------------------------------------------------
## This is the main code for calculating 2-D multipliers - wind direction = southeast 
## input DEM is stored in ../input
## outputs including smoothed and unsmoothed data are written in ../python_output
## more details in readme.txt

## 2013 Python code - W.Jiang
# --------------------------------------------------------
# import supporting modules
# --------------------------------------------------------
import os
from os.path import join, exists
import numpy
import math
import ascii_read      # read DEM data
import make_path       # generate indices of a data line depending on the direction
import multiplier_calc # calculate the multipliers for a data line extracted from the dataset

direction = 'se'
# --------------------------------------------------------
# check direction specification
# define output directory. If it does not exist, make one.
# --------------------------------------------------------
direction = direction.strip().lower()
valid = {'n','s','e','w','ne','nw','se','sw'}
if direction not in valid:
    raise Exception("Error: invalid direction given, must be one of n,s,e,w,ne,nw,se,sw")
    
mh_data_dir = '../python_output/'
if not os.path.exists(mh_data_dir):
    os.makedirs(mh_data_dir)

# --------------------------------------------------------
# read input data using ascii_read
# note: data was flattened to a single array
# --------------------------------------------------------
print'Reading data...\n'

nr = ascii_read.nrows
nc = ascii_read.ncols
xll = ascii_read.xllcorner
yll = ascii_read.yllcorner
cellsize = ascii_read.cellsize
data =  ascii_read.data.flatten()

# --------------------------------------------------------
# adjust cellsize for diagonal lines
# --------------------------------------------------------
data_spacing = ascii_read.cellsize

if len(direction) == 2:
   data_spacing = data_spacing*math.sqrt(2)

print 'xll = ',  xll
print 'yll = ',  yll
print 'data_spacing =',  data_spacing
# --------------------------------------------------------
# Compute the starting positions along the boundaries depending on dir 
# Together, the direction and the starting position determines a line.
# Note that the starting positions are defined
# in terms of the 1-d index of the array.
# --------------------------------------------------------
strt_idx = []

if direction.find('n') >= 0:
     strt_idx = numpy.append(strt_idx,list(range(0,nr*nc,nr)))
if direction.find('s') >= 0:
      strt_idx =  numpy.append(strt_idx,list(range(nr-1,nr*nc,nr)))
if direction.find('e') >= 0:
      strt_idx =  numpy.append(strt_idx,list(range((nc-1)*nr,nr*nc)))
if direction.find('w') >= 0:
      strt_idx =  numpy.append(strt_idx,list(range(0,nr)))
   
# --------------------------------------------------------
# for the diagonal directions the corner will have 
# been counted twice so get rid of the duplicate
# then loop over the data lines (i.e. over the starting positions)
# --------------------------------------------------------
strt_idx = numpy.unique(strt_idx)

ctr = 1    # counter in order to report progress 

for idx in strt_idx:

      print 'processing path %3i' % ctr+' of %3i' % len(strt_idx)+', index %5i.' % idx
       
      # get a line of the data
      # path is a 1-d vector which gives the indices of the data    
      path = make_path.make_path(nr,nc,idx,direction)
      line = data[path]
      
      # compute the multipliers
      M = multiplier_calc.multiplier_calc(line,data_spacing)

     # write the line back to the data array
      M = M.conj().transpose()
      data[path] = M[0,].flatten()
      ctr = ctr + 1

# --------------------------------------------------------
# reshape the result to matrix like 
# --------------------------------------------------------
data = numpy.reshape(data, (nc,nr))
data = data.conj().transpose()

# --------------------------------------------------------
# output unsmoothed data to an ascii file
# --------------------------------------------------------
ofn = join(mh_data_dir,'mh_'+ direction + '.asc')
print 'outputting unsmoothed data to: ', ofn

fid = open(ofn,'w')

fid.write('ncols         '+str(nc)+'\n')
fid.write('nrows         '+str(nr)+'\n')
fid.write('xllcorner     '+str(xll)+'\n')
fid.write('yllcorner     '+str(yll)+'\n')
fid.write('cellsize       '+str(cellsize)+'\n')
fid.write('NOdata_struct_value  -9999\n')

numpy.savetxt(fid, data, fmt ='%4.2f', delimiter = ' ', newline = '\n') 

# --------------------------------------------------------
# output smoothed data to an ascii file
# --------------------------------------------------------

ofn = join(mh_data_dir,'mh_'+ direction + '_smooth.asc')
print 'outputting smoothed data to: ', ofn
 
fid = open(ofn,'w')
fid.write('ncols         '+str(nc)+'\n')
fid.write('nrows         '+str(nr)+'\n')
fid.write('xllcorner     '+str(xll)+'\n')
fid.write('yllcorner     '+str(yll)+'\n')
fid.write('cellsize       '+str(cellsize)+'\n')
fid.write('NOdata_struct_value  -9999\n')

data_row = numpy.zeros((nr,nc),dtype=float)
# --------------------------------------------------------
# write top row
# --------------------------------------------------------
data_row[0,0] = (data[0,0]+data[0,1]+data[1,0])/3

for j in range(1, nc-1):
    data_row[0,j] = (data[0,j-1]+data[0,j]+data[0,j+1])/3
    
data_row[0,nc-1] = (data[0,nc-2]+data[0,nc-1]+data[1,nc-1])/3

# --------------------------------------------------------
# write general rows
# --------------------------------------------------------
for i in range(1,nr-1):
    data_row[i,0] = (data[i-1,0]+data[i,0]+data[i+1,0])/3
    
    for j in range(1,nc-1):
        data_row[i,j] = (data[i-1,j-1]+data[i-1,j]+data[i-1,j+1]+data[i,j-1]+data[i,j]+ data[i,j+1]+data[i+1,j-1]+data[i+1,j]+data[i+1,j+1])/9
    
    data_row[i,nc-1] = (data[i-1,nc-1]+data[i,nc-1]+data[i+1,nc-1])/3
    
# --------------------------------------------------------
# write bottom row
# --------------------------------------------------------
data_row[nr-1,0] = (data[nr-1,0]+data[nr-1,1]+data[nr-2,0])/3

for j in range(1,nc-1):
    data_row[nr-1,j] = (data[nr-1,j-1]+data[nr-1,j]+data[nr-1,j+1])/3
  
data_row[nr-1,nc-1] = (data[nr-1,nc-2]+data[nr-1,nc-1]+data[nr-2,nc-1])/3

numpy.savetxt(fid, data_row, fmt ='%4.2f', delimiter = ' ', newline = '\n') 

fid.close()

print'Finished\n'