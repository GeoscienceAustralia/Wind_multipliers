#!/usr/bin/env python

import numpy as np 
import gdal,osr
import struct 
import glob 
import os


#setting a search criteria for all tiff files that we want to use  - both needs to be in GDA94
LCCS_path= '/scratch/w85/nfm547/WM_Test/National/lccs_2015_L4_v-1.0.0_single_band.tif'


ds = gdal.Open(LCCS_path)
if ds is None:
    print ('Could not open the raster file')
    sys.exit(1)


# get raster size
cols = ds.RasterXSize # 1898
rows = ds.RasterYSize #2785
bands = ds.RasterCount #1
#Get raster metadata
geotransform = ds.GetGeoTransform()
#Get projection
prj = ds.GetProjection()
transform = ds.GetGeoTransform() # (2042525.0, 25.0, 0.0, -3174925.0, 0.0, -25.0)
xOrigin = transform[0] # 2042525.0
yOrigin = transform[3] # -3174925.0
pixelWidth = transform[1] # 25.0
pixelHeight = transform[5] # -25.0



band = ds.GetRasterBand(1)
number_band = 1



def changeRasterValues(band):

    fmttypes = {'Byte':'B', 'UInt16':'H', 'Int16':'h', 'UInt32':'I', 'Int32':'i', 'Float32':'f', 'Float64':'d'}

    data_type = band.DataType #1

    BandType = gdal.GetDataTypeName(band.DataType)  #Byte

    raster = []

    for y in range(band.YSize):

        scanline = band.ReadRaster(0, y, band.XSize, 1, band.XSize, 1, data_type)
        values = struct.unpack(fmttypes[BandType] * band.XSize, scanline)
        raster.append(values)

    raster = [ list(item) for item in raster ]

    #changing raster values
    for i, item in enumerate(raster):
        for j, value in enumerate(item):
            if (value >= 73) and (value <= 78):
                raster[i][j] = 305

    #transforming list in array
    raster = np.asarray(raster)

    return raster


driver = gdal.GetDriverByName("GTiff")
raster = changeRasterValues(band);


output_path = "/scratch/w85/nfm547/WM_develop/output_Australia/raster_output_Australia.tif"

dst_ds = driver.Create(output_path, 
                       band.XSize, 
                       band.YSize, 
                       number_band, 
                       band.DataType)


dst_ds.GetRasterBand(number_band).WriteArray(raster);


dst_ds.SetGeoTransform(geotransform);

# setting spatial reference of output raster 
srs = osr.SpatialReference(wkt = prj)
dst_ds.SetProjection( srs.ExportToWkt());


#Close output raster dataset 
dst_ds = None
#Close main raster dataset
ds = None

