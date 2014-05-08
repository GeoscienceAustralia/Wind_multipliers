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
        
        #log.info('convolution filter width ' + str(filter_width))
        
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
        ncobj.createDimension('x', outdata.shape[0])
        ncobj.createDimension('y', outdata.shape[1])
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
    
    if cyclone_area == 'no':
        mz_init = value_lookup.mz_init_non_cycl
    if cyclone_area == 'yes':
        mz_init = value_lookup.mz_init_cycl   
    
    outdata = np.zeros_like(data, np.float32)
    
    # Reclassify the land classes into initial terrain multipliers  
    for i in mz_init.keys():
        outdata[data == i] = mz_init[i]/1000.0
        
        
#    for i in range(data.shape[0]):            
#        for jj in range(data.shape[1]):
#            flag = 0
#            for terrain_class in mz_init.keys():
#                if data[i,jj] == terrain_class:
#                    outdata[i,jj] = mz_init[terrain_class]/1000.0
#                    flag = 1
#                    break
#            if flag == 0:
#                outdata[i,jj] = 1.0
   
    return outdata
    
    
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
