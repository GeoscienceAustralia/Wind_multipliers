"""
:mod:`shielding` -- Calculate shielding multiplier
==================================================================================

This module is called by the module 
:term:`all_multipliers` to calculate the shielding multiplier for an input tile
for 8 directions and output as NetCDF format.

References:
    
    Yang, T., Nadimpalli, K. & Cechet, R.P. 2014. Local wind assessment 
    in Australia: computation methodology for wind multipliers. Record 2014/33. 
    Geoscience Australia, Canberra.

:moduleauthor: Tina Yang <tina.yang@ga.gov.au>

""" 
    
# Import system & process modules
import sys, os, logging as log
import numexpr
from scipy import ndimage
from os.path import join as pjoin
import numpy as np
from osgeo.gdalconst import *
from osgeo import gdal
from utilities import value_lookup
from utilities.get_pixel_size_grid import get_pixel_size_grids, RADIANS_PER_DEGREE
from utilities.nctools import saveMultiplier, getLatLon



def shield(terrain, input_dem):
    """
    Performs core calculations to derive the shielding multiplier
    
    Parameters:        
    ----------- 

    :param terrain: `file` the input tile of the terrain class map (landcover). 
    :param input_dem:`file` the input tile of the DEM
    
    """ 
    
#    import pdb
#    pdb.set_trace()    
    
    log.info('Derive slope and reclassified aspect ...   ')
    slope_array, aspect_array = get_slope_aspect(input_dem)
    
    log.info('Reclassfy the terrain classes into initial shielding factors ...')
    ms_orig = terrain_class2ms_orig(terrain)

    log.info('Moving average and combine the slope and aspect for each direction ...')
    convo_combine(ms_orig, slope_array, aspect_array)
    
    os.remove(ms_orig)
    del slope_array, aspect_array
    
    log.info( 'finish shielding multiplier computation for this tile successfully')
   

def reclassify_aspect(data):
    """
    Reclassify the aspect valus from 0 ~ 360 to 1 ~ 9
    
    Parameters:        
    ----------- 
   
    :param data: :class:`numpy.ndarray` the input aspect values 0 ~ 360
    
    Returns:        
    --------  
        
    :outdata: :class:`numpy.ndarray` the output aspect values 1 ~ 9
    """   
    
#    import pdb
#    pdb.set_trace() 
    
    outdata = np.zeros_like(data, dtype = np.int)
    outdata.fill(9)    
       
    outdata[np.where((data >= 0 ) & (data < 22.5))] = 1    
    outdata[np.where((337.5 <= data) & (data <= 360))] = 1
    
    for i in range(2, 9):
        outdata[np.where((22.5 + (i-2)*45 <= data) & (data < 67.5 + (i-2)*45))] = i    
   
    return outdata
    

def get_slope_aspect(input_dem):
    """
    Calculate the slope and aspect from the input DEM
    
    Parameters:        
    ----------- 
   
    :param input_dem: `file` the input DEM
    
    Returns:        
    --------  
        
    :slope_array: :class:`numpy.ndarray` the output slope values
    :aspect_array_reclassify: :class:`numpy.ndarray` the output aspect values
    """ 
    
#    import pdb
#    pdb.set_trace() 
   
    np.seterr(divide='ignore')
    
    ds = gdal.Open(input_dem)    
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    geotransform = ds.GetGeoTransform()
    pixel_x_size = abs(geotransform[1]) 
    pixel_y_size = abs(geotransform[5])
    band = ds.GetRasterBand(1)     
    elevation_array = band.ReadAsArray(0, 0, cols, rows)
    elevation_array = elevation_array.astype(float)
    elevation_array[np.where(elevation_array < -0.001)] = np.nan
   
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

    
    
    ms_folder = pjoin(os.path.dirname(input_dem), 'shielding')
    file_name = os.path.basename(input_dem)
    driver = gdal.GetDriverByName('HFA')
    
    slope = pjoin(ms_folder, os.path.splitext(file_name)[0] + '_slope.img')    
    slope_ds = driver.Create(slope, ds.RasterXSize, ds.RasterYSize, 1, GDT_Float32)
    slope_ds.SetGeoTransform(ds.GetGeoTransform())
    slope_ds.SetProjection(ds.GetProjection()) 
    
    outBand_slope = slope_ds.GetRasterBand(1)
    outBand_slope.WriteArray(slope_array)
    
    # flush data to disk, set the NoData value and calculate stats
    outBand_slope.FlushCache()
    outBand_slope.SetNoDataValue(-99)
    outBand_slope.GetStatistics(0,1)
    
    
    aspect = pjoin(ms_folder, os.path.splitext(file_name)[0] + '_aspect.img')    
    aspect_ds = driver.Create(aspect, ds.RasterXSize, ds.RasterYSize, 1, GDT_Float32)
    aspect_ds.SetGeoTransform(ds.GetGeoTransform())
    aspect_ds.SetProjection(ds.GetProjection()) 
    
    outBand_aspect = aspect_ds.GetRasterBand(1)
    outBand_aspect.WriteArray(aspect_array_reclassify)
    
    # flush data to disk, set the NoData value and calculate stats
    outBand_aspect.FlushCache()
    outBand_aspect.SetNoDataValue(-99)
    outBand_aspect.GetStatistics(0,1)
    
    
    ds = None
    
    return slope_array, aspect_array_reclassify
    
   
def terrain_class2ms_orig(terrain): 
    """
    Reclassify the terrain classes into initial shielding factors
    
    Parameters:        
    ----------- 
   
    :param input_dem: `file` the input terrain class map
    
    Returns:        
    --------  
        
    :ms_orig: `file` the output initial shielding value map
    """   
#    import pdb
#    pdb.set_trace()     
    
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
    
    outdata = np.ones_like(data, dtype = np.float32)
                
    for i in [1, 3, 4, 5]:
        outdata[data == i] = ms_init[i]/100.0
      
    outdata[np.where(data==0)] = np.nan
    
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
    Apply convolution to the orginal shielding factor for each direction and call
    the :term:`combine` module to consider the slope and aspect and remove the 
    conservitism to get final shielding multiplier values
    
    Parameters:        
    ----------- 
   
    :param ms_orig: `file` the original shidelding factor map
    :param slope_array: :class:`numpy.ndarray` the input slope values
    :param aspect_array_reclassify: :class:`numpy.ndarray` the input aspect values
    
    """ 
#    import pdb
#    pdb.set_trace() 
    
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
    
    band = ms_orig_ds.GetRasterBand(1)     
    data = band.ReadAsArray(0, 0, cols, rows)
   
    if ms_orig_ds is None:
        log.info('Could not open %s ' % ms_orig)
        sys.exit(1)
    
    x_m_array, y_m_array = get_pixel_size_grids(ms_orig_ds)
    pixelWidth = 0.5 * (np.mean(x_m_array) + np.mean(y_m_array))
    
    log.info('pixelWidth is %2i ' %pixelWidth)
    
    ms_folder = os.path.dirname(ms_orig)
    nc_folder = pjoin(ms_folder, 'netcdf')
    file_name = os.path.basename(ms_orig)            
        
    dire = ['w', 'e', 'n', 's', 'nw', 'ne', 'se', 'sw']

    for one_dir in dire:

        log.info(one_dir)
        if one_dir in ['w', 'e', 'n', 's']:
            kernel_size = int(100.0/pixelWidth)
        else:
            kernel_size = int(100.0/pixelWidth)
            
        log.info('convolution kernel size is %s ' % str(kernel_size)) 
        
        # if the resolution size is bigger than 100 m, no covolution just copy 
        # the initial shielding factor to each direction
        if kernel_size > 0: 
            outdata = np.zeros((rows, cols), np.float32)
    
            kern_dir = globals()['kern_' + one_dir]
            mask = kern_dir(kernel_size)
#            print one_dir
#            print mask
            outdata = blur_image(data, mask) 
        else:             
            outdata = data            
            
        result = combine(outdata, slope_array, aspect_array, one_dir) 
        del outdata 
        
        # output format as netCDF4       
        tile_nc = pjoin(nc_folder, os.path.splitext(file_name)[0] + '_' + one_dir + '.nc')
        log.info("Saving terrain multiplier in netCDF file")   
        saveMultiplier('Ms', result, lat, lon, tile_nc)
        
        del result

    ms_orig_ds = None
   


def combine(ms_orig_array, slope_array, aspect_array, one_dir):
    """
    Used for each direction to derive the shielding multipliers by considering
    slope and aspect after covolution in the previous step. It also will remove 
    the conservatism.   
    
    Parameters:        
    ----------- 
   
    :param ms_orig_array: :class:`numpy.ndarray` convoluted initial shidelding values
    :param slope_array: :class:`numpy.ndarray` the input slope values
    :param aspect_array_reclassify: :class:`numpy.ndarray` the input aspect values
    
    Returns:        
    --------  
        
    :out_ms: :class:`numpy.ndarray` the output shielding mutipler values
    """
#    import pdb
#    pdb.set_trace() 
    
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
    (2*size+1, 2*size+1), it is south west direction
    
    Parameters:        
    ----------- 
   
    :param size: `int` the buffer size of the convolution 
    
    Returns:        
    --------  
        
    :class:`numpy.ndarray` the output kernel used for convolution
    """
    kernel = np.zeros((2*size+1, 2*size+1))
    kernel[size, size] = 1.0
    
    for i in range(1, size + 1):
        kernel[i-1:size, size + i] = 1.0   
    
    return kernel / kernel.sum()


def init_kern(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is north direction
    
    Parameters:        
    ----------- 
   
    :param size: `int` the buffer size of the convolution 
    
    Returns:        
    --------  
        
    :class:`numpy.ndarray` the output kernel used for convolution
    """ 
      
    kernel = np.zeros((2*size+1, 2*size+1))
    
    for i in range(0, size+1):
        kernel[i+size, size] = 1.0
    for i in range(2, size+1):
        kernel[size+i:, size-1:size+2] = 1.0  
    
    return kernel / kernel.sum()


def kern_w(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is west direction
    
    Parameters:        
    ----------- 
   
    :param size: `int` the buffer size of the convolution 
    
    Returns:        
    --------  
        
    :class:`numpy.ndarray` the output kernel used for convolution
    """ 
    
    return np.rot90(init_kern(size), 1)


def kern_e(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is east direction
    
    Parameters:        
    ----------- 
   
    :param size: `int` the buffer size of the convolution 
    
    Returns:        
    --------  
        
    :class:`numpy.ndarray` the output kernel used for convolution
    """ 
    
    return np.rot90(init_kern(size), 3)    


def kern_n(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is north direction
    
    Parameters:        
    ----------- 
   
    :param size: `int` the buffer size of the convolution 
    
    Returns:        
    --------  
        
    :class:`numpy.ndarray` the output kernel used for convolution
    """      
    
    return init_kern(size)


def kern_s(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is south direction
    
    Parameters:        
    ----------- 
   
    :param size: `int` the buffer size of the convolution 
    
    Returns:        
    --------  
        
    :class:`numpy.ndarray` the output kernel used for convolution
    """       
    
    return np.rot90(init_kern(size), 2)


def kern_ne(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is north-east direction
    
    Parameters:        
    ----------- 
   
    :param size: `int` the buffer size of the convolution 
    
    Returns:        
    --------  
        
    :class:`numpy.ndarray` the output kernel used for convolution
    """    
    
    return np.flipud(np.fliplr(init_kern_diag(size)))


def kern_nw(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is north-west direction
    
    Parameters:        
    ----------- 
   
    :param size: `int` the buffer size of the convolution 
    
    Returns:        
    --------  
        
    :class:`numpy.ndarray` the output kernel used for convolution
    """   
    
    return np.flipud(init_kern_diag(size))    


def kern_sw(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is south-west direction
    
    Parameters:        
    ----------- 
   
    :param size: `int` the buffer size of the convolution 
    
    Returns:        
    --------  
        
    :class:`numpy.ndarray` the output kernel used for convolution
    """  
        
    return init_kern_diag(size)


def kern_se(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is south-east direction
    
    Parameters:        
    ----------- 
   
    :param size: `int` the buffer size of the convolution 
    
    Returns:        
    --------  
        
    :class:`numpy.ndarray` the output kernel used for convolution
    """      
    
    return np.fliplr(init_kern_diag(size))


def blur_image(im, kernel, mode='constant'):
    """
    Blurs the image by convolving with a kernel (e.g. mean or gaussian) of typical
    size n. The optional keyword argument ny allows for a different size in the
    y direction.
    
    Parameters:        
    ----------- 
   
    :param im: :class:`numpy.ndarray` the input data of initial shielding values
    :param kernel: :class:`numpy.ndarray` the kernel used for convolution
    
    Returns:        
    --------  
        
    :class:`numpy.ndarray` the output data afer convolution
    """     
    #improc = signal.convolve(im, kernel, mode=mode)
    improc = ndimage.convolve(im, kernel, mode=mode, cval=1.0)
    return(improc)


if __name__ == '__main__':
    dem = '/nas/gemd/climate_change/CHARS/B_Wind/Projects/Multipliers/validation/output_work/test_dem.img'
    terrain = '/nas/gemd/climate_change/CHARS/B_Wind/Projects/Multipliers/validation/output_work/test_terrain.img'
    shield(terrain, dem)
