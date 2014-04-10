#!/usr/bin/python2.6
import numpy
import sys
from osgeo import gdal
from osgeo.gdalconst import *

"""
.. module:: read_output.py
   :synopsis: Module used to read in DEM file, and convert data to numpy array

.. moduleauthor:: Daniel Wild <daniel.wild@ga.gov.au>


"""
def read(inputfile):
    """Reads an input file, loops through adding its content to a numpy array

    Args:
        inputFile (str): The path to an input file (DEM).
        e.g. 'test_topographic/topo_expected_output/mh_n.asc'

    Returns:
         A numpy array
    """

    # debug - permit print whole numpy array
    # numpy.set_printoptions(threshold=numpy.nan)

    inDs = gdal.Open(inputfile, GA_ReadOnly)
    if inDs is None:
      print 'Could not open %s'%inputfile
      sys.exit(1)

    # get raster size
    rows = inDs.RasterYSize
    cols = inDs.RasterXSize

    # create empty numpy array
    data = numpy.zeros((rows,cols),dtype=numpy.float)

    # get the bands and block sizes
    inBand = inDs.GetRasterBand(1)

    #resolution = inDs.GetGeoTransform()[1]
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

    return data
