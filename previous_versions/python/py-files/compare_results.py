## --------------------------------------------------------
## Compare outputs from the Python code and the Octave code
## --------------------------------------------------------

import numpy
import output_py
import output_oct, ascii_read
import pdb
import os
from os.path import join, exists

direction = 'ne'
# --------------------------------------------------------
# check direction specification
# define output directory. If it does not exist, make one.
# --------------------------------------------------------
direction = direction.strip().lower()
valid = {'n','s','e','w','ne','nw','se','sw'}
if direction not in valid:
    raise Exception("Error: invalid direction given, must be one of n,s,e,w,ne,nw,se,sw")
    
mh_data_dir = '../comparison_output/'
if not os.path.exists(mh_data_dir):
    os.makedirs(mh_data_dir)

A = output_py.data
B = output_oct.data
comp = A - B
rows = output_py.nrows
cols = output_py.ncols
# pdb.set_trace()
n = 0
for i in range(0,rows):
    for j in range(0,cols):
        if comp[[i],[j]] >= [0.01] or comp[[i],[j]] <= [-0.01]:
            n = n+1
            print 'comp[[i],[j]] = ', i, j, comp[[i],[j]]
            print 'A = ', A[[i],[j]]
            print 'B = ', B[[i],[j]]


ofn = join(mh_data_dir,'comp_mh_'+ direction + '.asc')
print 'outputting comparison to: ', ofn

nr = ascii_read.nrows
nc = ascii_read.ncols
xll = ascii_read.xllcorner
yll = ascii_read.yllcorner
cellsize = ascii_read.cellsize

fid = open(ofn,'w')
fid.write('ncols         '+str(nc)+'\n')
fid.write('nrows         '+str(nr)+'\n')
fid.write('xllcorner     '+str(xll)+'\n')
fid.write('yllcorner     '+str(yll)+'\n')
fid.write('cellsize       '+str(cellsize)+'\n')
fid.write('NOdata_struct_value  -9999\n')

numpy.savetxt(fid, comp, fmt ='%4.2f', delimiter = ' ', newline = '\n')            
#             raise Exception("Incorrect results!")
# #              print 'Incorrect results!'
print 'no of inconsistence = ', n                
print 'Correct results!'
