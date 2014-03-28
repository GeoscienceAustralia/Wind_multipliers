##------------------------------------------------------
## Read input DEM stored in ../input 
##------------------------------------------------------
import numpy
# -----------------------
# read input ascii file
#------------------------
input_dem = '../input/dem.asc'

fid = open(input_dem,'r')

if fid == -1:
     raise Exception("Cannot find file")
 
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
        xllcorner     = float(data_str)
    elif i == 4:  
        yllcorner     = float(data_str)
    elif i == 5:
        cellsize      = float(data_str)
    elif i == 6:
        NODATA_value  = int(data_str)
 
# Read dataset

A = numpy.zeros([nrows, ncols], dtype=float)

for i in xrange(nrows):
            row = numpy.zeros([ncols])    
            line = fid.readline()
 
            for j, val in enumerate(line.split(), start = 0):
                value = float(val)
                if value == NODATA_value:
                    #value = Nan
                    value = numpy.nan
                row[j] = value
            A[i,:] = row
fid.close()

A = A.conj().transpose()
max_data = A.max()
nan_ind = numpy.isnan(A)

A[nan_ind] = max_data
NODATA_value = max_data

data = A

