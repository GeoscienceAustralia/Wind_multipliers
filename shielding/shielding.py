# ---------------------------------------------------------------------------
# Purpose: transfer the landsat classied image into shielding multplier
# Input: loc, input raster file format: loc + '_terrain_class.img', dem
# Output: loc + '_ms' in each direction
# Created on 12 08 2011 by Tina Yang
# ---------------------------------------------------------------------------



    
# Import system & process modules
import sys, string, os, time, logging as log
import numexpr
from scipy import ndimage, signal
from os.path import join as pjoin
import numpy as np
from osgeo.gdalconst import *
from netCDF4 import Dataset
from osgeo import gdal
from utilities import value_lookup
from utilities.get_pixel_size_grid import get_pixel_size_grids, RADIANS_PER_DEGREE
from utilities.nctools import saveMultiplier, getLatLon


#RADIANS_PER_DEGREE = 0.01745329251994329576923690768489

def shield(terrain, input_dem):    
    # start timing
    startTime = time.time()   
 
    log.info('Derive slope and reclassified aspect ...   ')
    slope_array, aspect_array = get_slope_aspect(input_dem)
    
    log.info('Reclassfy the terrain classes into initial shielding factors ...')
    ms_orig = terrain_class2ms_orig(terrain)

    log.info('Moving average and combine the slope and aspect for each direction ...')
    convo_combine(ms_orig, slope_array, aspect_array)
    
    os.remove(ms_orig)
    del slope_array, aspect_array
    
    log.info( 'finish shielding multiplier computation for this tile successfully')

    # figure out how long the script took to run
    stopTime = time.time()
    sec = stopTime - startTime
    days = int(sec / 86400)
    sec -= 86400*days
    hrs = int(sec / 3600)
    sec -= 3600*hrs
    mins = int(sec / 60)
    sec -= 60*mins
    log.info('The scipt took %3i ' % days + 'days, %2i ' % hrs + 'hours, %2i ' % mins + 'minutes %.2f ' %sec + 'seconds')




def reclassify_aspect(data):
    """
    Purpose: transfer the landsat classied image into original terrain multplier
    Input: loc, input raster file format: loc + '_terrain_class.img', cyclone_area -yes or -no
    Output: loc + '_mz_orig'
    """
        
    outdata = np.zeros_like(data, dtype = np.int)
    outdata.fill(9)    
       
    outdata[np.where((data >= 0 ) & (data < 22.5))] = 1    
    outdata[np.where((337.5 <= data) & (data <= 360))] = 1
    
    for i in range(2, 9):
        outdata[np.where((22.5 + (i-2)*45 <= data) & (data < 67.5 + (i-2)*45))] = i    
   
    return outdata
    

def get_slope_aspect(input_dem):
    
    ds = gdal.Open(input_dem)    
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    geotransform = ds.GetGeoTransform()
    pixel_x_size = abs(geotransform[1]) 
    pixel_y_size = abs(geotransform[5])
    band = ds.GetRasterBand(1)     
    elevation_array = band.ReadAsArray(0, 0, cols, rows)   
   
    x_m_array, y_m_array = get_pixel_size_grids(ds)
    
    dzdx_array = ndimage.sobel(elevation_array, axis=1)/(8. * pixel_x_size)
    dzdx_array = numexpr.evaluate("dzdx_array * pixel_x_size / x_m_array")
    del x_m_array
    
    dzdy_array = ndimage.sobel(elevation_array, axis=0)/(8. * pixel_y_size)
    dzdy_array = numexpr.evaluate("dzdy_array * pixel_y_size / y_m_array")
    del y_m_array    
    
    # Slope    
    hypotenuse_array = np.hypot(dzdx_array, dzdy_array)
    slope_array = numexpr.evaluate("arctan(hypotenuse_array) / RADIANS_PER_DEGREE")
    del hypotenuse_array          
    
    # Aspect
    # Convert angles from conventional radians to compass heading 0-360
    aspect_array = numexpr.evaluate("(450 - arctan2(dzdy_array, -dzdx_array) / RADIANS_PER_DEGREE) % 360")
    # Derive reclassifed aspect...    
    aspect_array_reclassify = reclassify_aspect(aspect_array)
    del aspect_array       

    ds = None
    
    return slope_array, aspect_array_reclassify
    
   
def terrain_class2ms_orig(terrain): 

    ms_folder = pjoin(os.path.dirname(terrain), 'shielding')
    file_name = os.path.basename(terrain)
    # output format as ERDAS Imagine
    driver = gdal.GetDriverByName('HFA')
    
    # open the tile
    terrain_resample_ds = gdal.Open(terrain)
    
    # get image size, format, projection
    cols = terrain_resample_ds.RasterXSize
    rows = terrain_resample_ds.RasterYSize
    
    # get georeference info    
    band = terrain_resample_ds.GetRasterBand(1)     
    data = band.ReadAsArray(0, 0, cols, rows)
    
    ms_init = value_lookup.ms_init 
    
    outdata = np.ones_like(data)
                
    for i in [1, 3, 4, 5]:
        outdata[data == i] = ms_init[i]/100.0
      
    ms_orig = pjoin(ms_folder, os.path.splitext(file_name)[0] + '_ms.img')    
    ms_orig_ds = driver.Create(ms_orig, terrain_resample_ds.RasterXSize, terrain_resample_ds.RasterYSize, 1, GDT_Float32)
    ms_orig_ds.SetGeoTransform(terrain_resample_ds.GetGeoTransform())
    ms_orig_ds.SetProjection(terrain_resample_ds.GetProjection()) 
    
    outBand_ms_orig = ms_orig_ds.GetRasterBand(1)
    outBand_ms_orig.WriteArray(outdata)
    del outdata
    
    # flush data to disk, set the NoData value and calculate stats
    outBand_ms_orig.FlushCache()
    outBand_ms_orig.SetNoDataValue(-99)
    outBand_ms_orig.GetStatistics(0,1)
    
    terrain_resample_ds = None
    
    return ms_orig
    
    


def convo_combine(ms_orig, slope_array, aspect_array):
    """
    apply convolution to the orginal shielding factor for each direction
    input: ms_orig.img
    outputs: shield_east.img, shield_west.img, ..., shield_sw.img etc.
    """  
    
    ms_orig_ds = gdal.Open(ms_orig)    
    
    # get image size, format, projection
    cols = ms_orig_ds.RasterXSize
    rows = ms_orig_ds.RasterYSize
    
    geotransform = ms_orig_ds.GetGeoTransform()
    x_Left = geotransform[0]
    y_Upper = -geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = -geotransform[5]
    
    lon, lat = getLatLon(x_Left, y_Upper, pixelWidth, pixelHeight, cols, rows)
    
    # get georeference info    
    band = ms_orig_ds.GetRasterBand(1)     
    data = band.ReadAsArray(0, 0, cols, rows)
   
    if ms_orig_ds is None:
        log.info('Could not open %s ' % ms_orig)
        sys.exit(1)
    
    x_m_array, y_m_array = get_pixel_size_grids(ms_orig_ds)
    pixelWidth = 0.5 * (np.mean(x_m_array) + np.mean(y_m_array))
    
    log.info('pixelWidth is %2i ' %pixelWidth)
    
    ms_folder = os.path.dirname(ms_orig)
    raster_folder = pjoin(ms_folder, 'raster')
    nc_folder = pjoin(ms_folder, 'netcdf')
    file_name = os.path.basename(ms_orig)            
        
    dire = ['w', 'e', 'n', 's', 'nw', 'ne', 'se', 'sw']

    for one_dir in dire:

        log.info(one_dir)
        output_dir = pjoin(raster_folder, os.path.splitext(file_name)[0] +  '_' + one_dir + '.img')

        if one_dir in ['w', 'e', 'n', 's']:
            kernel_size = int(100.0/pixelWidth)
        else:
            kernel_size = int(100.0/pixelWidth)
            
        log.info('convolution kernel size is %s ' % str(kernel_size)) 
        
        # if the resolution size is bigger than 100 m, no covolution just copy the initial shielding factor to each direction
        if kernel_size > 0: 
            outdata = np.zeros((rows, cols), np.float32)
    
            kern_dir = globals()['kern_' + one_dir]
            mask = kern_dir(kernel_size)
            outdata = blur_image(data, mask) 
        else:             
            outdata = data            
            
        result = combine(outdata, slope_array, aspect_array, one_dir) 
        del outdata 
        
        # output format as ERDAS Imagine
        driver = gdal.GetDriverByName('HFA')
        ms_dir_ds = driver.Create(output_dir, ms_orig_ds.RasterXSize, ms_orig_ds.RasterYSize, 1, GDT_Float32)
        
        # georeference the image and set the projection                           
        ms_dir_ds.SetGeoTransform(ms_orig_ds.GetGeoTransform())
        ms_dir_ds.SetProjection(ms_orig_ds.GetProjection()) 
        
        outBand_ms_dir = ms_dir_ds.GetRasterBand(1)
        outBand_ms_dir.WriteArray(result)       
        
        # flush data to disk, set the NoData value and calculate stats
        outBand_ms_dir.FlushCache()
        outBand_ms_dir.SetNoDataValue(-99)
        #outBand_ms_dir.ComputeStatistics(1)
        outBand_ms_dir.GetStatistics(0,1) 
        
        ms_dir_ds = None
        
        # output format as netCDF4       
        tile_nc = pjoin(nc_folder, os.path.splitext(file_name)[0] + '_' + one_dir + '.nc')
        
        log.info("Saving terrain multiplier in netCDF file")   
        saveMultiplier('Ms', result, lat, lon, tile_nc)
        
#        ncobj = Dataset(tile_nc, 'w', format='NETCDF4', clobber=True)
#        # create the x and y dimensions
#        ncobj.createDimension('x', result.shape[1])
#        ncobj.createDimension('y', result.shape[0])
#        #create the variable (Shielding multpler ms in float)
#        nc_data = ncobj.createVariable('ms', np.dtype(float), ('x', 'y'))
#        # write data to variable
#        nc_data[:] = result
#        #close the file
#        ncobj.close()
        del result

    ms_orig_ds = None
   


def combine(ms_orig_array, slope_array, aspect_array, one_dir):
    """
    To Generate Shielding Multiplier. This tool will be used for each direction to
    derive the shielding multipliers after moving averaging the shielding multiplier using direction_filter.py
    It also will remove the conservatism. 
    input: slope, reclassified aspect, shield origin in one direction
    output: shielding multiplier in the dirction
    """           
    
    dire_aspect = value_lookup.dire_aspect
    aspect_value = dire_aspect[one_dir]
    
    conservatism = 0.9
    up_degree = 12.30
    low_degree = 3.27
    
    out_ms = ms_orig_array
    
    slope_uplimit = np.where((slope_array >= 12.30) & (aspect_array == aspect_value))
    slope_middle = np.where((slope_array > 3.27 ) & (slope_array < 12.30) & (aspect_array == aspect_value))
    
    out_ms[slope_uplimit] = 1.0
    out_ms[slope_middle]  = ((1.0 - ms_orig_array[slope_middle]) * (slope_array[slope_middle] - low_degree)/(up_degree - low_degree)) + ms_orig_array[slope_middle] 
    
    ms_smaller = np.where(out_ms < conservatism)
    ms_bigger = np.where(out_ms >= conservatism)
    out_ms[ms_smaller] = out_ms[ms_smaller] * conservatism
    out_ms[ms_bigger] = out_ms[ms_bigger]**2
    
    return out_ms
    

   
def init_kern_diag(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is north east direction
    """
    kernel = np.zeros((2*size+1, 2*size+1))
    kernel[size, size] = 1.0
    
    for i in range(1, size + 1):
        kernel[i-1:size, size + i] = 1.0   
    
    return kernel / kernel.sum()


def init_kern(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is south direction
    """       
    kernel = np.zeros((2*size+1, 2*size+1))
    
    for i in range(0, size+1):
        kernel[i+size, size] = 1.0
    for i in range(2, size+1):
        kernel[size+i:, size-1:size+2] = 1.0  
    
    return kernel / kernel.sum()


def kern_w(size):
##    print np.rot90(init_kern(size), 3)    
    return np.rot90(init_kern(size), 3)


def kern_e(size):
##    print np.rot90(init_kern(size), 1)    
    return np.rot90(init_kern(size), 1)    


def kern_n(size):
##    print np.rot90(init_kern(size), 2)    
    return np.rot90(init_kern(size), 2)


def kern_s(size):
##    print init_kern(size)    
    return init_kern(size)


def kern_ne(size):
##    print init_kern_diag(size)    
    return init_kern_diag(size)


def kern_nw(size):
##    print np.fliplr(init_kern_diag(size))    
    return np.fliplr(init_kern_diag(size))


def kern_sw(size):
##    print np.flipud(np.fliplr(init_kern_diag(size)))    
    return np.flipud(np.fliplr(init_kern_diag(size)))


def kern_se(size):
##    print np.flipud(init_kern_diag(size))    
    return np.flipud(init_kern_diag(size))


def blur_image(im, kernel, mode='same'):
    """
    Blurs the image by convolving with a kernel (e.g. mean or gaussian) of typical
    size n. The optional keyword argument ny allows for a different size in the
    y direction.
    """     
    improc = signal.convolve(im, kernel, mode=mode)
    return(improc)


if __name__ == '__main__':
    dem = '/nas/gemd/climate_change/CHARS/B_Wind/Projects/Multipliers/validation/output_work/test_dem.img'
    terrain = '/nas/gemd/climate_change/CHARS/B_Wind/Projects/Multipliers/validation/output_work/test_terrain.img'
    shield(terrain, dem)
