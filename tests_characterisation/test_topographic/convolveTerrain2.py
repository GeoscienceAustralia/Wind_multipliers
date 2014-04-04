# import modules
import os, numpy, sys, time, pdb
from osgeo import gdal, ogr
from osgeo.gdalconst import *

'''

It opens the file:

inDs = gdal.Open( inputFile, GA_ReadOnly)

and then loops through the rows/columns to put the data into a
numpy array in blocks, the size of which are an attribute of the input dataset:

# read the data in:
dd = inBand.ReadAsArray(j, i, numCols, numRows).astype(numpy.float)

# do the calculations:
data[i:i+numRows, j:j+numCols] = dd

It then does the calculations and writes the data back out in GeoTiff format,
applying the geographic transformation and projection information (if any) from
the original dataset.


'''


filename = os.environ.get('PYTHONSTARTUP')
if filename and os.path.isfile(filename):
    execfile(filename)
from convolve import convolve


startTime = time.time()

###---EDIT FOR SHIELDING------###
#inputDir = "C:/yolanda2013_postassessment/MULTIPLIER/shielding"
#inputFile = "ms_origproj"
#outputPath = "C:/yolanda2013_postassessment/MULTIPLIER/shielding"

###---EDIT FOR TERRAIN------###
#inputDir = "C:/yolanda2013_postassessment/MULTIPLIER/terrain"
#inputFile = "smarmz_origp"
#outputPath = "C:/yolanda2013_postassessment/MULTIPLIER/terrain"

inputDir = '/nas/gemd/climate_change/CHARS/G_Users/u12161/data/GMMA/Multipliers'
inputFile = 'ms_orig'
outputPath = '/nas/gemd/climate_change/CHARS/G_Users/u12161/data/GMMA/Multipliers'

directions = ['N','NE','W','NW','S','SW','E','SE'] 

# Multiplier type:

####---EDIT---
#mType = "terrain" # or "shield"
mType = "shield" # or "terrain"

if mType=="terrain":
    mTabbrev = "mz"
elif mType=="shield":
    mTabbrev = "shield"

# set the working directory
os.chdir(inputDir)

# register all of the GDAL drivers
gdal.AllRegister()

# open the image - start with the terrain multiplier:
inDs = gdal.Open( inputFile, GA_ReadOnly)
if inDs is None:
  print 'Could not open %s'%inputFile
  sys.exit(1)

# get image size
rows = inDs.RasterYSize
cols = inDs.RasterXSize
bands = inDs.RasterCount

data = numpy.ones((rows,cols),dtype=numpy.float)

# get the bands and block sizes
inBand = inDs.GetRasterBand(1)
resolution = inDs.GetGeoTransform()[1]
blockSizes = inBand.GetBlockSize()
xBlockSize = blockSizes[0]
yBlockSize = blockSizes[1]



# loop through the rows
for i in range(0, rows, yBlockSize):
    if i + yBlockSize < rows:
        numRows = yBlockSize
    else:
        numRows = rows - i

  # loop through the columns
    for j in range(0, cols, xBlockSize):
        if j + xBlockSize < cols:
            numCols = xBlockSize
        else:
            numCols = cols - j
    
        # read the data in
        dd = inBand.ReadAsArray(j, i, numCols, numRows).astype(numpy.float)
    
        # do the calculations
        data[i:i+numRows, j:j+numCols] = dd

for d in directions:
    dTime = time.time()
    print "Running convolution..."
    outdata = convolve(data, d, mType, resolution)
    print "Writing data to file..."

    outputFile = os.path.join( outputPath, '%s_%s.img'%( mTabbrev, d ) )

    # create the output image - default to a GeoTIFF
    driver = gdal.GetDriverByName('GTiff')
    outDs = driver.Create(outputFile, cols, rows, 1, GDT_Float32)
    if outDs is None:
        print 'Could not create %s'%outputFile
        sys.exit(1)
    outBand = outDs.GetRasterBand( 1 )

    outBand.WriteArray(outdata, 0, 0 ) 
    
    # flush data to disk, set the NoData value and calculate stats
    outBand.FlushCache()
    outBand.SetNoDataValue(-9999)
    stats = outBand.GetStatistics(0, 1)

    # georeference the image and set the projection to match 
    # the input dataset
    outDs.SetGeoTransform(inDs.GetGeoTransform())
    outDs.SetProjection(inDs.GetProjection())

    # build pyramids
    gdal.SetConfigOption('USE_RRD', 'YES')
    outDs.BuildOverviews(overviewlist=[2,4,8,16,32,64,128])

    # Close the output file:
    outDs = None
    print 'Time to process %s: %6.1f'%(d, time.time() - dTime )

# Close the input dataset object:
inDs = None

print 'script took', time.time() - startTime, 'seconds to run'
