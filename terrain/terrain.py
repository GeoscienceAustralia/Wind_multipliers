# ---------------------------------------------------------------------------
# Purpose: to derive the terrain multplier
# Input: loc, input raster file format: loc + '_terrain_class.img'
#        cyclone_area -yes or -no
# Output: loc + '_mz_orig'
# Created on 12 08 2011 by Tina Yang
# ---------------------------------------------------------------------------

    
# Import system & process modules

import sys, string, os, time, shutil, logging as log
import value_lookup
import numpy as np, osgeo.gdal as gdal
from osgeo.gdalconst import *
from netCDF4 import Dataset
from os.path import join as pjoin
from scipy import signal


def terrain(cyclone_area, temp_tile):
    # start timing
    startTime = time.time()
    
    # open the tile
    temp_dataset = gdal.Open(temp_tile) 
    #temp_dataset = temp_tile
    
    # get image size, format, projection
    cols = temp_dataset.RasterXSize
    rows = temp_dataset.RasterYSize
    bands = temp_dataset.RasterCount
    log.info('Input raster format is %s' % temp_dataset.GetDriver().ShortName + '/ %s' % temp_dataset.GetDriver().LongName)
    log.info('Image size is %s' % cols + 'x %s' % rows + 'x %s' % bands)
    
    # get georeference info
    geotransform = temp_dataset.GetGeoTransform()
    pixelWidth = geotransform[1]    
    band = temp_dataset.GetRasterBand(1)     
    data = band.ReadAsArray(0, 0, cols, rows)
       
    # produce the original terrain multipler from the input terrain classified image   
    log.info('Reclassfy the terrain classes into initial terrain multipliers ...')
    reclassified_array = terrain_class2mz_orig(cyclone_area, data)

    # convoulution of the original terrain multipler into different directions
    log.info('Moving average for each direction ...')
    # convolute for each direction
    dire = ['w', 'e', 'n', 's', 'nw', 'ne', 'se', 'sw']



    for one_dir in dire:
        log.info(one_dir)
        if one_dir in ['w', 'e', 'n', 's']:
            filter_width = int(0.01/pixelWidth)- 1
        else:
            filter_width = int(0.01/(pixelWidth*1.414))+ 1
        
        if filter_width > reclassified_array.shape[0]:
            filter_width = reclassified_array.shape[0]
        
        log.info('convolution filter width ' + str(filter_width))
        
#        kern_dir = globals()['kern_' + one_dir]
#        mask = kern_dir(filter_width)
#        outdata = blur_image(reclassified_array, mask) 
        
        convo_dir = globals()['convo_' + one_dir]
        outdata = convo_dir(reclassified_array, filter_width)  

        # find output folder
        tile_folder = os.path.dirname(temp_tile)
        file_name = os.path.basename(temp_tile)
        
#        import pdb
#        pdb.set_trace()
        
        # output format as ERDAS Imagine
        img_folder = pjoin(pjoin(tile_folder, 'terrain'), 'raster')
        driver = gdal.GetDriverByName('HFA')
        output_dir = pjoin(img_folder, os.path.splitext(file_name)[0] + '_mz_' + one_dir + '.img')
        #output_dir = pjoin(mz_folder, 'test_mz_' + one_dir + '.img')
        output_img = driver.Create(output_dir, cols, rows, 1, GDT_Float32)
        # georeference the image and set the projection
        output_geotransform = temp_dataset.GetGeoTransform()                                 
        output_img.SetGeoTransform(output_geotransform)
        output_img.SetProjection(temp_dataset.GetProjection())
        
        outBand = output_img.GetRasterBand(1)
        outBand.WriteArray(outdata, 0, 0)
    
        # flush data to disk, set the NoData value and calculate stats
        outBand.FlushCache()
        outBand.SetNoDataValue(-99)
        outBand.GetStatistics(0,1)
    
        # output format as netCDF4
        nc_folder = pjoin(pjoin(tile_folder, 'terrain'), 'netcdf')
        tile_nc = pjoin(nc_folder, os.path.splitext(file_name)[0] + '_mz_' + one_dir + '.nc')
        ncobj = Dataset(tile_nc, 'w', format='NETCDF4', clobber=True)
        # create the x and y dimensions
        ncobj.createDimension('x', outdata.shape[1])
        ncobj.createDimension('y', outdata.shape[0])
        #create the variable (Terrain multpler mz in float)
        data = ncobj.createVariable('mz', np.dtype(float), ('x', 'y'))
        # write data to variable
        data[:] = outdata
        #close the file
        ncobj.close()
        
    
        del outdata
        
        output_img = None
        
    temp_dataset = None
    
    log.info('finish terrain multiplier computation for this tile successfully')    

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



def terrain_class2mz_orig(cyclone_area, data):
    """
    Purpose: transfer the landsat classied image into original terrain multplier
    Input: loc, input raster file format: loc + '_terrain_class.img', cyclone_area -yes or -no
    Output: loc + '_mz_orig'
    """
       
#    data = np.array([[2,4,4,5,13,11],
#                      [7,14,3,1,8,6],
#                      [1,9,4,7,2,18],
#                      [2,5,15,12,7,8],
#                      [3,8,3,1,5,2],
#                      [2,9,4,15,1,3]])
#    
#    cycl = np.array([[1,0,0,0,0,0],
#                              [0,0,0,1,0,0],
#                              [0,0,0,0,0,0],
#                              [0,0,0,0,0,0],
#                              [0,0,0,1,0,0],
#                              [0,0,0,0,1,0]])
#                             
#    cyclone_area = 'Yes'                             
       
    
    mz_init = value_lookup.mz_init_non_cycl
    mz_init_cycl = value_lookup.mz_init_cycl 

    outdata = np.zeros_like(data, np.float32)    
    
    # Reclassify the land classes into initial terrain multipliers 
    for i in mz_init.keys():
        outdata[data == i] = mz_init[i]/1000.0
    
#    import pdb
#    pdb.set_trace()
    
    if cyclone_area <> None:
        dataset = gdal.Open(cyclone_area)
        cols = dataset.RasterXSize
        rows = dataset.RasterYSize
        band = dataset.GetRasterBand(1)     
        cycl = band.ReadAsArray(0, 0, cols, rows)
        
        for i in mz_init_cycl.keys():
            cycl_loc = np.where((data == i) & (cycl == 1))
            outdata[cycl_loc] = mz_init_cycl[i]/1000.0
              
        dataset = None
    return outdata
    
 
#def init_kern_diag(size):
#    """
#    Returns a mean kernel for convolutions, with dimensions
#    (2*size+1, 2*size+1), it is north east direction
#    """    
#    
#    kernel = np.zeros((2*size+1, 2*size+1))
#    kernel[size, size] = 1.0
#    
#    for i in range(0, size + 1):
#        kernel[size-i, size + i] = 1.0
#        
##    kernel[size-3:size, size+1] = 1.0
##    kernel[size-2:size, size+2] = 1.0
##    kernel[size-1, size+3] = 1.0    
#    
#    return kernel / kernel.sum()
#
#
#def init_kern(size):
#    """
#    Returns a mean kernel for convolutions, with dimensions
#    (2*size+1, 2*size+1), it is south direction
#    """       
#    kernel = np.zeros((2*size+1, 2*size+1))
#    
#    for i in range(0, size+1):
#        kernel[i+size, size] = 1.0
#    
#    return kernel / kernel.sum()
#
#
#def kern_w(size):
###    print np.rot90(init_kern(size), 3)    
#    return np.rot90(init_kern(size), 3)
#
#
#def kern_e(size):
#    print np.rot90(init_kern(size), 1)    
#    return np.rot90(init_kern(size), 1)    
#
#
#def kern_n(size):
###    print np.rot90(init_kern(size), 2)    
#    return np.rot90(init_kern(size), 2)
#
#
#def kern_s(size):
###    print init_kern(size)    
#    return init_kern(size)
#
#
#def kern_ne(size):
#    print init_kern_diag(size)    
#    return init_kern_diag(size)
#
#
#def kern_nw(size):
###    print np.fliplr(init_kern_diag(size))    
#    return np.fliplr(init_kern_diag(size))
#
#
#def kern_sw(size):
###    print np.flipud(np.fliplr(init_kern_diag(size)))    
#    return np.flipud(np.fliplr(init_kern_diag(size)))
#
#
#def kern_se(size):
###    print np.flipud(init_kern_diag(size))    
#    return np.flipud(init_kern_diag(size))
#
#
#def blur_image(im, kernel, mode='same'):
#    """
#    Blurs the image by convolving with a kernel (e.g. mean or gaussian) of typical
#    size n. The optional keyword argument ny allows for a different size in the
#    y direction.
#    """     
#    improc = signal.convolve(im, kernel, mode=mode)
#    return(improc)
   
## calculate the west direction
def convo_w(data, filter_width): 
#    import pdb
#    pdb.set_trace()
    
    outdata = np.zeros_like(data, np.float32)
    rows = data.shape[0]
    cols = data.shape[1]    
    
    for i in range(rows):        
    # calculate average for each pixel    
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


## calculate the east direction
def convo_e(data, filter_width):    
    outdata = np.zeros_like(data, np.float32)
    rows = data.shape[0]
    cols = data.shape[1]
    
    for i in range(rows):         
    # calculate average for each pixel    
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


## calculate the north direction
def convo_n(data, filter_width):
    outdata = np.zeros_like(data, np.float32)
    rows = data.shape[0]
    cols = data.shape[1]
    
    for i in range(cols):        
    # calculate average for each pixel    
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


## calculate the south direction
def convo_s(data, filter_width):
    outdata = np.zeros_like(data, np.float32)
    rows = data.shape[0]
    cols = data.shape[1]
    
    for i in range(cols):        
    # calculate average for each pixel    
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


## calculate the north west direction
def convo_nw(data, filter_width):
    outdata = np.zeros_like(data, np.float32)
    rows = data.shape[0]
    cols = data.shape[1]
    
    for i in range(rows):        
    # calculate average for each pixel    
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


## calculate the north east direction
def convo_ne(data, filter_width):
    outdata = np.zeros_like(data, np.float32)
    rows = data.shape[0]
    cols = data.shape[1]
   
    for i in range(rows):        
    # calculate average for each pixel    
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


## calculate the south west direction
def convo_sw(data, filter_width):
    outdata = np.zeros_like(data, np.float32)
    rows = data.shape[0]
    cols = data.shape[1]
    
    for i in range(rows):        
    # calculate average for each pixel    
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


## calculate the south east direction
def convo_se(data, filter_width):
    outdata = np.zeros_like(data, np.float32)
    rows = data.shape[0]
    cols = data.shape[1]
    
    for i in range(rows):        
    # calculate average for each pixel    
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


##if __name__ == '__main__':
##    config = ConfigParser.RawConfigParser()
##    config.read('terr_shield.cfg')
##
##    root = config.get('input_values', 'root')
##    loc_list = config.get('input_values', 'loc_list').split()
##    cyclone_area = config.get('input_values', 'cyclone_area')
##    terrain(root, loc_list, cyclone_area)

#
#if __name__ == '__main__':
#    print kern_w(4)

if __name__ == '__main__':
    cyclone = r'N:\climate_change\CHARS\B_Wind\Projects\Multipliers\validation\output_work\test_cycl_stat.img'
    terr = r'N:\climate_change\CHARS\B_Wind\Projects\Multipliers\validation\output_work\test_terr_resamp.img'
    terrain(cyclone, terr)