import os
from os.path import join as pjoin, exists
import numpy as np
import math
import logging as log
from scipy import signal
from osgeo import gdal, osr
from netCDF4 import Dataset
from osgeo.gdalconst import *

from vincenty import vinc_dist
from blrb import interpolate_grid

import make_path       
import multiplier_calc 

__version__ = '0.4 - intergarate with terrian ans shileding multiplier for tiling and parallelisation'

RADIANS_PER_DEGREE = 0.01745329251994329576923690768489


class earth(object):

    # Mean radius
    RADIUS = 6371009.0  # (metres)

    # WGS-84
    #RADIUS = 6378135.0  # equatorial (metres)
    #RADIUS = 6356752.0  # polar (metres)

    # Length of Earth ellipsoid semi-major axis (metres)
    SEMI_MAJOR_AXIS = 6378137.0

    # WGS-84
    A = 6378137.0           # equatorial radius (metres)
    B = 6356752.3142        # polar radius (metres)
    F = (A - B) / A         # flattening
    ECC2 = 1.0 - B**2/A**2  # squared eccentricity

    MEAN_RADIUS = (A*2 + B) / 3

    # Earth ellipsoid eccentricity (dimensionless)
    #ECCENTRICITY = 0.00669438
    #ECC2 = math.pow(ECCENTRICITY, 2)

    # Earth rotational angular velocity (radians/sec)
    OMEGA = 0.000072722052


def get_pixel_size(dataset, (x, y)):
    """
    Returns X & Y sizes in metres of specified pixel as a tuple.
    N.B: Pixel ordinates are zero-based from top left
    """
    log.debug('(x, y) = (%f, %f)', x, y)
    
    spatial_reference = osr.SpatialReference()
    spatial_reference.ImportFromWkt(dataset.GetProjection())
    
    geotransform = dataset.GetGeoTransform()
    log.debug('geotransform = %s', geotransform)
    
    latlong_spatial_reference = spatial_reference.CloneGeogCS()
    coord_transform_to_latlong = osr.CoordinateTransformation(spatial_reference, latlong_spatial_reference)

    # Determine pixel centre and edges in georeferenced coordinates
    xw = geotransform[0] + x * geotransform[1]
    yn = geotransform[3] + y * geotransform[5] 
    xc = geotransform[0] + (x + 0.5) * geotransform[1]
    yc = geotransform[3] + (y + 0.5) * geotransform[5] 
    xe = geotransform[0] + (x + 1.0) * geotransform[1]
    ys = geotransform[3] + (y + 1.0) * geotransform[5] 
    
    log.debug('xw = %f, yn = %f, xc = %f, yc = %f, xe = %f, ys = %f', xw, yn, xc, yc, xe, ys)
    
    # Convert georeferenced coordinates to lat/lon for Vincenty
    lon1, lat1, _z = coord_transform_to_latlong.TransformPoint(xw, yc, 0)
    lon2, lat2, _z = coord_transform_to_latlong.TransformPoint(xe, yc, 0)
    log.debug('For X size: (lon1, lat1) = (%f, %f), (lon2, lat2) = (%f, %f)', lon1, lat1, lon2, lat2)
    x_size, _az_to, _az_from = vinc_dist(earth.F, earth.A, 
                                         lat1 * RADIANS_PER_DEGREE, lon1 * RADIANS_PER_DEGREE, 
                                         lat2 * RADIANS_PER_DEGREE, lon2 * RADIANS_PER_DEGREE)
    
    lon1, lat1, _z = coord_transform_to_latlong.TransformPoint(xc, yn, 0)
    lon2, lat2, _z = coord_transform_to_latlong.TransformPoint(xc, ys, 0)
    log.debug('For Y size: (lon1, lat1) = (%f, %f), (lon2, lat2) = (%f, %f)', lon1, lat1, lon2, lat2)
    y_size, _az_to, _az_from = vinc_dist(earth.F, earth.A, 
                                         lat1 * RADIANS_PER_DEGREE, lon1 * RADIANS_PER_DEGREE, 
                                         lat2 * RADIANS_PER_DEGREE, lon2 * RADIANS_PER_DEGREE)
    
    log.debug('(x_size, y_size) = (%f, %f)', x_size, y_size)
    return (x_size, y_size)


def get_pixel_size_grids(dataset):
    """ Returns two grids with interpolated X and Y pixel sizes for given datasets"""
       
    def get_pixel_x_size(x, y):
        #return get_pixel_size(dataset, (x, y))[0]
        return get_pixel_size(dataset, (x, y))[1]
    
    def get_pixel_y_size(x, y):
        #return get_pixel_size(dataset, (x, y))[1]
        return get_pixel_size(dataset, (x, y))[0]
    
    #x_size_grid = np.zeros((dataset.RasterXSize, dataset.RasterYSize)).astype(np.float32)
    x_size_grid = np.zeros((dataset.RasterYSize, dataset.RasterXSize)).astype(np.float32)
    interpolate_grid(depth=1, shape=x_size_grid.shape, eval_func=get_pixel_x_size, grid=x_size_grid)

    #y_size_grid = np.zeros((dataset.RasterXSize, dataset.RasterYSize)).astype(np.float32)
    y_size_grid = np.zeros((dataset.RasterYSize, dataset.RasterXSize)).astype(np.float32)
    interpolate_grid(depth=1, shape=y_size_grid.shape, eval_func=get_pixel_y_size, grid=y_size_grid)
    
    return (x_size_grid, y_size_grid)


def topomult(input_dem):

    """
    Executes core topographic multiplier functionality

    :param input_dem: The path for input DEM

    """    
   
   # find output folder
    mh_folder = pjoin(os.path.dirname(input_dem), 'topographic')
    file_name = os.path.basename(input_dem)
    raster_folder = pjoin(mh_folder, 'raster')
    nc_folder = pjoin(mh_folder, 'netcdf')        
    
    ds = gdal.Open(input_dem)    
    nc = ds.RasterXSize
    nr = ds.RasterYSize
    band = ds.GetRasterBand(1)     
    elevation_array = band.ReadAsArray(0, 0, nc, nr)
    elevation_array_tran = np.transpose(elevation_array)        
    data =  elevation_array_tran.flatten()
    
    x_m_array, y_m_array = get_pixel_size_grids(ds)
    cellsize = 0.5 * (np.mean(x_m_array) + np.mean(y_m_array))    
       
    # Compute the starting positions along the boundaries depending on dir 
    # Together, the direction and the starting position determines a line.
    # Note that the starting positions are defined
    # in terms of the 1-d index of the array.
    
    directions = ['n','s','e','w','ne','nw','se','sw']
    #directions = ['s']
    
    for direction in directions:
        log.info(direction)        
        
        if len(direction) == 2:
            data_spacing = cellsize*math.sqrt(2)
        else:
            data_spacing = cellsize
            
        Mhdata = np.ones(data.shape)
        strt_idx = []    
        if direction.find('n') >= 0:
            strt_idx = np.append(strt_idx, list(range(0, nr * nc, nr)))
        if direction.find('s') >= 0:
            strt_idx =  np.append(strt_idx, list(range(nr - 1, nr * nc, nr)))
        if direction.find('e') >= 0:
            strt_idx =  np.append(strt_idx, list(range((nc - 1) * nr, nr * nc)))
        if direction.find('w') >= 0:
            strt_idx =  np.append(strt_idx, list(range(0, nr)))
           
        # For the diagonal directions the corner will have been counted twice 
        # so get rid of the duplicates then loop over the data lines 
        # (i.e. over the starting positions)
        strt_idx = np.unique(strt_idx)
        
        for ctr, idx in enumerate(strt_idx):
            log.debug( 'Processing path %3i' % ctr+' of %3i' % len(strt_idx)+', index %5i.' % idx )
           
            # Get a line of the data
            # path is a 1-d vector which gives the indices of the data    
            path = make_path.make_path(nr, nc, idx, direction)
            line = data[path]
            M = multiplier_calc.multiplier_calc(line, data_spacing)
              
            # write the line back to the data array
            #M = M.conj().transpose()
            M = np.transpose(M)
            Mhdata[path] = M[0,].flatten()
               
    
        # Reshape the result to matrix like 
        Mhdata = np.reshape(Mhdata, (nc, nr))
        #Mhdata = Mhdata.conj().transpose()
        Mhdata = np.transpose(Mhdata)
        
        g = np.ones((3, 3))/9.
        
#        mhsmooth = signal.convolve2d(Mhdata, g, mode='same', boundary='fill', 
#                                     fillvalue=1)
        mhsmooth = signal.convolve(Mhdata, g, mode='same')
        del Mhdata
               
        # output format as ERDAS Imagine
        driver = gdal.GetDriverByName('HFA')
        output_dir = pjoin(raster_folder, os.path.splitext(file_name)[0] +  '_' + direction + '.img')
        ms_dir_ds = driver.Create(output_dir, ds.RasterXSize, ds.RasterYSize, 1, GDT_Float32)
        
        # georeference the image and set the projection                           
        ms_dir_ds.SetGeoTransform(ds.GetGeoTransform())
        ms_dir_ds.SetProjection(ds.GetProjection()) 
        
        outBand_ms_dir = ms_dir_ds.GetRasterBand(1)
        outBand_ms_dir.WriteArray(mhsmooth)       
        
        # flush data to disk, set the NoData value and calculate stats
        outBand_ms_dir.FlushCache()
        outBand_ms_dir.SetNoDataValue(-99)
        #outBand_ms_dir.ComputeStatistics(1)
        outBand_ms_dir.GetStatistics(0,1) 
        
        ms_dir_ds = None
        
        # output format as netCDF4       
        tile_nc = pjoin(nc_folder, os.path.splitext(file_name)[0] + '_' + direction + '.nc')
        ncobj = Dataset(tile_nc, 'w', format='NETCDF4', clobber=True)
        # create the x and y dimensions
        ncobj.createDimension('x', mhsmooth.shape[1])
        ncobj.createDimension('y', mhsmooth.shape[0])
        #create the variable (Shielding multpler ms in float)
        nc_data = ncobj.createVariable('ms', np.dtype(float), ('x', 'y'))
        # write data to variable
        nc_data[:] = mhsmooth
        #close the file
        ncobj.close()
        del mhsmooth
        
        log.info('Finished direction %s' % direction)
        
    ds = None

   
if __name__ == '__main__': 
    #dem = r'N:\climate_change\CHARS\B_Wind\Projects\Multipliers\validation\output_work\test_dem.img'
    dem = '/nas/gemd/climate_change/CHARS/B_Wind/Projects/Multipliers/validation/output_work/small_dem_4_int.img'
    #dem = r'N:\climate_change\CHARS\B_Wind\Projects\Multipliers\validation\output_work\test_dem.asc'
    topomult(dem)
