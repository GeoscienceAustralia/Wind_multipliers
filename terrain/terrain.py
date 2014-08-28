"""
:mod:`terrain` -- Calculate terrain multiplier
==================================================================================

This module is called by the module 
:term:`all_multipliers` to calculate the terrain multiplier for an input tile
for 8 directions and output as NetCDF format.

References:
    
    Yang, T., Nadimpalli, K. & Cechet, R.P. 2014. Local wind assessment 
    in Australia: computation methodology for wind multipliers. Record 2014/33. 
    Geoscience Australia, Canberra.

:moduleauthor: Tina Yang <tina.yang@ga.gov.au>

""" 
    
# Import system & process modules
import os, logging as log
from utilities import value_lookup
from utilities.nctools import saveMultiplier, getLatLon
from utilities.get_pixel_size_grid import get_pixel_size_grids
import numpy as np, osgeo.gdal as gdal
#from osgeo.gdalconst import *
from os.path import join as pjoin


def terrain(cyclone_area, temp_tile):
    """
    Performs core calculations to derive the terrain multiplier
    
    Parameters:        
    ----------- 

    :param cyclone_area: none or `file` the input tile of the cyclone area file. 
    :param temp_tile:`file` the image file of the input tile of the land cover
    
    """
#    import pdb
#    pdb.set_trace()
#    
    # open the tile
    temp_dataset = gdal.Open(temp_tile)
    
    # get image size, format, projection
    cols = temp_dataset.RasterXSize
    rows = temp_dataset.RasterYSize
    bands = temp_dataset.RasterCount
    log.info('Input raster format is %s' % temp_dataset.GetDriver().ShortName + 
            '/ %s' % temp_dataset.GetDriver().LongName)
    log.info('Image size is %s' % cols + 'x %s' % rows + 'x %s' % bands)
    
    # get georeference info
    geotransform = temp_dataset.GetGeoTransform()
    x_Left = geotransform[0]
    y_Upper = -geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = -geotransform[5]
    
    # get the tile's longitude and latitude values used to save output in netcdf
    lon, lat = getLatLon(x_Left, y_Upper, pixelWidth, pixelHeight, cols, rows)
    
    # get the average grid size in metre of the tile
    x_m_array, y_m_array = get_pixel_size_grids(temp_dataset)
    pixelWidth = 0.5 * (np.mean(x_m_array) + np.mean(y_m_array))
    log.info('pixelWidth is %2i ' %pixelWidth)
    print pixelWidth    
    
    # produce the original terrain multiplier from the input terrain map   
    log.info('Reclassfy the terrain classes into initial terrain multipliers ...')
    band = temp_dataset.GetRasterBand(1)      
    data = band.ReadAsArray(0, 0, cols, rows)
    reclassified_array = terrain_class2mz_orig(cyclone_area, data)
    # if the value is 0, it is nodata
    reclassified_array[reclassified_array==0] = np.nan

    # convoulution of the original terrain multipler into different directions
    log.info('Moving average for each direction ...')
    #dire = ['w', 'e', 'n', 's', 'nw', 'ne', 'se', 'sw']  
    dire = ['w'] 
    
    #set the terrain buffer used for convolution as per AS/NZ 1170.2 (2011)
    terrain_buffer = 1000.    

    for one_dir in dire:
        log.info(one_dir)
        if one_dir in ['w', 'e', 'n', 's']:
            filter_width = int(terrain_buffer/pixelWidth)
        else:
            filter_width = int(terrain_buffer/(pixelWidth*1.414))
        
        # if the tile is smaller than the upwind buffer, all the tile is in buffer
        if filter_width > reclassified_array.shape[0]:
            filter_width = reclassified_array.shape[0]
        
        log.info('convolution filter width ' + str(filter_width))
        
        convo_dir = globals()['convo_' + one_dir]
        outdata = convo_dir(reclassified_array, filter_width) 
                     
        # find output folder
        tile_folder = os.path.dirname(temp_tile)
        file_name = os.path.basename(temp_tile)        
    
        # output format as netCDF4        
        nc_folder = pjoin(pjoin(tile_folder, 'terrain'), 'netcdf')
        tile_nc = pjoin(nc_folder, os.path.splitext(file_name)[0] + '_mz_' + one_dir + '.nc')
        log.info("Saving terrain multiplier in netCDF file")   
        saveMultiplier('Mz', outdata, lat, lon, tile_nc)        
    
        del outdata
        
    temp_dataset = None
    
    log.info('finish terrain multiplier computation for this tile successfully') 


def terrain_class2mz_orig(cyclone_area, data):
    """
    Transfer the landsat classified image into original terrain multiplier
    
    Parameters:        
    ----------- 

    :param cyclone_area: none or `file` the input tile of the cyclone area file
    :param data: :class:`numpy.ndarray` the input terrain class values
    
    Returns:        
    --------  
        
    :returns: :class:`numpy.ndarray` the initial terrain multiplier value
    """                
    
    # if the cyclone_area is empty, the cyclone value is 0
    # otherwise, the cyclone value is taken from the cyclone area file passed
    
    cycl = np.zeros_like(data, np.float32)
    
    if cyclone_area <> None:
        dataset = gdal.Open(cyclone_area)
        cols = dataset.RasterXSize
        rows = dataset.RasterYSize
        band = dataset.GetRasterBand(1)     
        cycl = band.ReadAsArray(0, 0, cols, rows)     
        dataset = None
     
    return tc2mz_orig(cycl,data)  
     
 
def tc2mz_orig(cycl, data):
    """
    Transfer the landsat classified image into original terrain multiplier
    
    Parameters:        
    ----------- 

    :param cycl: :class:`numpy.ndarray` the cyclone value of the tile
    :param data: :class:`numpy.ndarray` the input terrain class values
    
    Returns:        
    --------  
        
    :outdata: :class:`numpy.ndarray` the initial terrain multiplier value
    """   
    
    mz_init = value_lookup.mz_init_non_cycl
    mz_init_cycl = value_lookup.mz_init_cycl 

    outdata = np.zeros_like(data, np.float32)    
    
    # Reclassify the land classes into initial terrain multipliers 
    for i in mz_init.keys():
        outdata[data == i] = mz_init[i]/1000.0     
           
    for i in mz_init_cycl.keys():
        cycl_loc = np.where((data == i) & (cycl == 1))
        outdata[cycl_loc] = mz_init_cycl[i]/1000.0              
        
    return outdata
    
    
def convo_w(data, filter_width): 
    """
    Convolute the initial terrain multplier to final one for west direction
    
    Parameters:        
    ----------- 

    :param data: :class:`numpy.ndarray` the initial terrain multiplier values
    :param filter_width: :`int` the number of cells within upwind buffer 
    
    Returns:        
    --------  
        
    :outdata: :class:`numpy.ndarray` the final terrain multiplier value
    """   
    
    outdata = np.zeros_like(data, np.float32)
    rows = data.shape[0]
    cols = data.shape[1]    
    
    # calculate average for each pixel 
    for i in range(rows):
        for jj in range(cols):            
            neighbour_sum = 0   
            # for pixels whose west neighbour amount is less than defined value.
            # e.g in terrian for each hori and vert direction, for 25m resolution, the amount is 39    
            if jj < filter_width:            
                for m in range(jj+1):
                    neighbour_sum += data[i, m]
                average = neighbour_sum / float(jj+1)
                    
            else:
                for m in range(jj-filter_width, jj+1):
                    neighbour_sum += data[i, m]
                average = neighbour_sum / (filter_width + 1)

            # get the calculated pixel value                 
            outdata[i, jj] = average
    return outdata


def convo_e(data, filter_width):  
    """
    Convolute the initial terrain multplier to final one for east direction
    
    Parameters:        
    ----------- 

    :param data: :class:`numpy.ndarray` the initial terrain multiplier values
    :param filter_width: :`int` the number of cells within upwind buffer 
    
    Returns:        
    --------  
        
    :outdata: :class:`numpy.ndarray` the final terrain multiplier value
    """   
    
    outdata = np.zeros_like(data, np.float32)
    rows = data.shape[0]
    cols = data.shape[1]
    
    # calculate average for each pixel
    for i in range(rows):
        for jj in range(cols):            
            neighbour_sum = 0   
            # for pixels whose east neighbour amount is less than defined value.
            # e.g in terrian for each hori and vert direction, for 25m resolution, the amount is 39
            starting_less = cols - filter_width            
            if jj >= starting_less:            
                for m in range(jj, cols):
                    neighbour_sum += data[i, m]
                average = neighbour_sum / float(cols - jj)                    
            else:
                for m in range(jj, jj + filter_width + 1):
                    neighbour_sum += data[i, m]
                average = neighbour_sum / (filter_width + 1)

            # get the calculated pixel value                 
            outdata[i, jj] = average
    return outdata


def convo_n(data, filter_width):
    """
    Convolute the initial terrain multplier to final one for north direction
    
    Parameters:        
    ----------- 

    :param data: :class:`numpy.ndarray` the initial terrain multiplier values
    :param filter_width: :`int` the number of cells within upwind buffer 
    
    Returns:        
    --------  
        
    :outdata: :class:`numpy.ndarray` the final terrain multiplier value
    """   
    
    outdata = np.zeros_like(data, np.float32)
    rows = data.shape[0]
    cols = data.shape[1]
    
    # calculate average for each pixel 
    for i in range(cols):  
        for jj in range(rows):            
            neighbour_sum = 0   
            # for pixels whose north neighbour amount is less than defined value.
            # e.g in terrian for each hori and vert direction, for 25m resolution, the amount is 39    
            if jj < filter_width:            
                for m in range(jj+1):
                    neighbour_sum += data[m, i]
                average = neighbour_sum / float(jj+1)                    
            else:
                for m in range(jj-filter_width, jj+1):
                    neighbour_sum += data[m, i]
                average = neighbour_sum / (filter_width + 1)
                
            # get the calculated pixel value                 
            outdata[jj, i] = average
    return outdata



def convo_s(data, filter_width):
    """
    Convolute the initial terrain multplier to final one for south direction
    
    Parameters:        
    ----------- 

    :param data: :class:`numpy.ndarray` the initial terrain multiplier values
    :param filter_width: :`int` the number of cells within upwind buffer 
    
    Returns:        
    --------  
        
    :outdata: :class:`numpy.ndarray` the final terrain multiplier value
    """   
    
    outdata = np.zeros_like(data, np.float32)
    rows = data.shape[0]
    cols = data.shape[1]
    
    # calculate average for each pixel     
    for i in range(cols):      
        for jj in range(rows):            
            neighbour_sum = 0   
            # for pixels whose south neighbour amount is less than defined value.
            # e.g in terrian for each hori and vert direction, for 25m resolution, the amount is 39
            starting_less = rows - filter_width            
            if jj >= starting_less:            
                for m in range(jj, rows):
                    neighbour_sum += data[m, i]
                average = neighbour_sum / float(rows - jj)                    
            else:
                for m in range(jj, jj + filter_width + 1):
                    neighbour_sum += data[m, i]
                average = neighbour_sum / (filter_width + 1)
    
            # get the calculated pixel value                
            outdata[jj, i] = average
    return outdata



def convo_nw(data, filter_width):
    """
    Convolute the initial terrain multplier to final one for north-west direction
    
    Parameters:        
    ----------- 

    :param data: :class:`numpy.ndarray` the initial terrain multiplier values
    :param filter_width: :`int` the number of cells within upwind buffer 
    
    Returns:        
    --------  
        
    :outdata: :class:`numpy.ndarray` the final terrain multiplier value
    """   
    
    outdata = np.zeros_like(data, np.float32)
    rows = data.shape[0]
    cols = data.shape[1]
    
    # calculate average for each pixel
    for i in range(rows): 
        for jj in range(cols):            
            neighbour_sum = 0   
            # for pixels whose north west neighbour amount is less than defined value.
            # e.g in terrian for each hori and vert direction, for 25m resolution, the amount is 29    
            less_boundary = min(i, jj)            
            if less_boundary < filter_width:            
                for m in range(less_boundary + 1):
                    neighbour_sum += data[i-m, jj-m]
                average = neighbour_sum / float(less_boundary+1)                    
            else:
                for m in range(filter_width+1):
                    neighbour_sum += data[i-m, jj-m]
                average = neighbour_sum / (filter_width + 1)

            # get the calculated pixel value                 
            outdata[i, jj] = average
    return outdata


def convo_ne(data, filter_width):
    """
    Convolute the initial terrain multplier to final one for north direction
    
    Parameters:        
    ----------- 

    :param data: :class:`numpy.ndarray` the initial terrain multiplier values
    :param filter_width: :`int` the number of cells within upwind buffer 
    
    Returns:        
    --------  
        
    :outdata: :class:`numpy.ndarray` the final terrain multiplier value
    """   
    
    outdata = np.zeros_like(data, np.float32)
    rows = data.shape[0]
    cols = data.shape[1]
   
    # calculate average for each pixel   
    for i in range(rows): 
        for jj in range(cols):            
            neighbour_sum = 0   
            # for pixels whose north east neighbour amount is less than defined value.
            # e.g in terrian for each hori and vert direction, for 25m resolution, the amount is 29    
            less_boundary = min(i, cols-jj-1)            
            if less_boundary < filter_width:            
                for m in range(less_boundary + 1):
                    neighbour_sum += data[i-m, jj+m]
                average = neighbour_sum / float(less_boundary+1)                    
            else:
                for m in range(filter_width+1):
                    neighbour_sum += data[i-m, jj+m]
                average = neighbour_sum / (filter_width + 1)

            # get the calculated pixel value                 
            outdata[i, jj] = average
    return outdata


def convo_sw(data, filter_width):
    """
    Convolute the initial terrain multplier to final one for south-west direction
    
    Parameters:        
    ----------- 

    :param data: :class:`numpy.ndarray` the initial terrain multiplier values
    :param filter_width: :`int` the number of cells within upwind buffer 
    
    Returns:        
    --------  
        
    :outdata: :class:`numpy.ndarray` the final terrain multiplier value
    """   
    
    outdata = np.zeros_like(data, np.float32)
    rows = data.shape[0]
    cols = data.shape[1]
    
    # calculate average for each pixel     
    for i in range(rows):  
        for jj in range(cols):            
            neighbour_sum = 0   
            # for pixels whose south west neighbour amount is less than defined value.
            # e.g in terrian for each hori and vert direction, for 25m resolution, the amount is 29    
            less_boundary = min(rows-i-1, jj)            
            if less_boundary < filter_width:            
                for m in range(less_boundary + 1):
                    neighbour_sum += data[i+m, jj-m]
                average = neighbour_sum / float(less_boundary+1)                    
            else:
                for m in range(filter_width+1):
                    neighbour_sum += data[i+m, jj-m]
                average = neighbour_sum / (filter_width + 1)

            # get the calculated pixel value                 
            outdata[i, jj] = average
    return outdata


def convo_se(data, filter_width):
    """
    Convolute the initial terrain multplier to final one for south-east direction
    
    Parameters:        
    ----------- 

    :param data: :class:`numpy.ndarray` the initial terrain multiplier values
    :param filter_width: :`int` the number of cells within upwind buffer 
    
    Returns:        
    --------  
        
    :outdata: :class:`numpy.ndarray` the final terrain multiplier value
    """   
    
    outdata = np.zeros_like(data, np.float32)
    rows = data.shape[0]
    cols = data.shape[1]
    
    # calculate average for each pixel 
    for i in range(rows):
        for jj in range(cols):            
            neighbour_sum = 0   
            # for pixels whose south east neighbour amount is less than defined value.
            # e.g in terrian for each hori and vert direction, for 25m resolution, the amount is 29    
            less_boundary = min(rows-i-1, cols-jj-1)            
            if less_boundary < filter_width:            
                for m in range(less_boundary + 1):
                    neighbour_sum += data[i+m, jj+m]
                average = neighbour_sum / float(less_boundary+1)                    
            else:
                for m in range(filter_width+1):
                    neighbour_sum += data[i+m, jj+m]
                average = neighbour_sum / (filter_width + 1)

            # get the calculated pixel value                
            outdata[i, jj] = average
    return outdata



if __name__ == '__main__':
    cyclone = r'N:\climate_change\CHARS\B_Wind\Projects\Multipliers\validation\output_work\test_cycl_stat.img'
    terr = r'N:\climate_change\CHARS\B_Wind\Projects\Multipliers\validation\output_work\test_terr_resamp.img'
    terrain(cyclone, terr)