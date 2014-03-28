## --------------------------------------------------------
## Read Python output file 
##--------------------------------------------------------
import numpy

output_py = '../python_output/mh_ne.asc'

fid = open(output_py,'r')

if fid == -1:
    raise Exception("Error: 'Cannot find file")
 
# Read header information and store in structure
for i in range(1,7):
    tline    = fid.readline()
    data_str = tline.partition(' ')[2]
#     print data_str
    if i == 1: 
       ncols         = int(data_str)
    elif i == 2:
        nrows         = int(data_str)
    elif i == 3:
        xllcorner     = str(data_str)
    elif i == 4:  
        yllcorner     = str(data_str)
    elif i == 5:
        cellsize      = str(data_str)
    elif i == 6:
        NODATA_value  = str(data_str)
 
# Read dataset

A = numpy.zeros([nrows, ncols], dtype=float)

for i in xrange(nrows):
            row = numpy.zeros([ncols])    
            line = fid.readline()
 
            for j, val in enumerate(line.split(), start = 0):
                row[j] = val
            A[i,:] = row
fid.close()

data = A