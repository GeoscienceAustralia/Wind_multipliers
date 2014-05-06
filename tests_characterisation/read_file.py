#!/usr/bin/python2.6
import numpy
import sys
from osgeo import gdal
from osgeo.gdalconst import *

"""
.. module:: read_file.py
   :synopsis: Module used to read input file, and convert data to numpy array

.. moduleauthor:: Daniel Wild <daniel.wild@ga.gov.au>


"""


def readASC(inputfile):
    """
    Reads .asc DEM into a GDALDataSet

    :param inputfile: The path to an input file (DEM)
    :returns: A numpy array
    """

    # debug - permit print whole numpy array
    # numpy.set_printoptions(threshold=numpy.nan)

    inDs = gdal.Open(inputfile, GA_ReadOnly)

    return convertToNumpyArray(inDs)


def readNetCDF(inputFile, ncVar):
    """
    Reads an NETCDF file into a GDALDataSet

    :param inputFile: The path to an input file (NETCDF)
    :param ncVar: The name of var to read from NETCDF file
    :returns: A numpy array
    """

    # DEBUG - permit print whole numpy array
    numpy.set_printoptions(threshold=numpy.nan)

    # DEBUG - meaningful errors
    gdal.UseExceptions()

    inDs = gdal.Open('NETCDF:"'+ inputFile+'":'+ncVar)

    return convertToNumpyArray(inDs)


def convertToNumpyArray(gdalDataSet):
    """
    Reads GDALDataSet into a numpy array

    :param gdalDataSet: a GDAL DataSet to be converted to numpy.array
    :returns: A numpy array
    """

    if gdalDataSet is None:
        print 'Could not open %s'%inputFile
        sys.exit(1)

    # get raster size
    rows = gdalDataSet.RasterYSize
    cols = gdalDataSet.RasterXSize

    # create empty numpy array
    data = numpy.zeros((rows,cols),dtype=numpy.float)

    # get the bands and block sizes
    inBand = gdalDataSet.GetRasterBand(1)

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

    # DEBUG
    print data

    return data