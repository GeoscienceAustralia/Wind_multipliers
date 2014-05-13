import arcpy
import math
from arcpy.sa import *
import os
import sys
import time
import numpy
import shutil

"""
.. module:: direction_filter.py
    :synopsis: Read input DEM stored in ../input
"""

def terrain_convo(loc, root):
    """
    Moving average in each direction the initial terrain multipliers to derive the terrain
    multipliers for each direction.

    Input: initial terrain multiplier (mz_orig) produced from module terrain_class2mz_orig.py
    :param loc:
    :param root:
    :returns: the terrain multiplier for each of the eight directions.
    """

    arcpy.env.overwriteOutput = True

    # set directory
    work_folder = root + '\\process\\terrain'
    os.chdir(work_folder)
    
    output_folder = root + '\\output\\terrain'

    # open the image 
    input_img = loc + '_mz_orig'
    ds = Raster(input_img)

    if ds is None:
        print 'Could not open ' + input_img
        sys.exit(1)

    # get image size, format, projection
    cols = ds.width
    rows = ds.height
    bands = ds.bandCount
    pixelWidth = ds.meanCellWidth
    pixelHeight = ds.meanCellHeight

    print 'Format: ', ds.format
    print 'Size is ',cols,'x',rows,'x',bands

    print 'extent: ', ds.extent
    print 'resolution ', pixelWidth, 'x', pixelHeight

    #sr = arcpy.Describe(ds).spatialReference
    sr = ds.spatialReference

    lowleft_corner = arcpy.Point(ds.extent.XMin,ds.extent.YMin)

    
    data = arcpy.RasterToNumPyArray(ds)
    

    dire = ['w', 'e', 'n', 's', 'nw', 'ne', 'se', 'sw']

    #dire = ['w']

    for one_dir in dire:

        print one_dir

        output_dir = output_folder + '\\' + loc + '_mz_' + one_dir + '.img'

        if one_dir in ['w', 'e', 'n', 's']:
            filter_width = int(math.ceil(1000/pixelWidth))- 1
        else:
            filter_width = int(math.ceil(1000/(pixelWidth*1.414)))+ 1

        print 'convolution filter width ' + str(filter_width)
      
        outdata = numpy.zeros((rows, cols), numpy.float32)
        convo_dir = globals()['convo_' + one_dir]
        outdata = convo_dir(data, rows, cols, outdata, filter_width)

        if arcpy.Exists(output_dir):
            arcpy.Delete_management(output_dir)

        arcpy.NumPyArrayToRaster(outdata, lowleft_corner, pixelWidth, pixelHeight).save(output_dir) 
        
        arcpy.DefineProjection_management(output_dir, sr)

        del outdata
             
    arcpy.BuildPyramidsandStatistics_management(output_folder, "#", "BUILD_PYRAMIDS", "CALCULATE_STATISTICS")

    ds = None
    del data  



def convo_w(data, rows, cols, outdata, filter_width):
    """
    Calculate the west direction

    :param data:
    :param rows:
    :param cols:
    :param outdata:
    :param filter_width:
    """

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


def convo_e(data, rows, cols, outdata, filter_width):
    """
    Calculate the east direction

    :param data:
    :param rows:
    :param cols:
    :param outdata:
    :param filter_width:
    """

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


def convo_n(data, rows, cols, outdata, filter_width):

    """
    Calculate the north direction

    :param data:
    :param rows:
    :param cols:
    :param outdata:
    :param filter_width:
    """

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


def convo_s(data, rows, cols, outdata, filter_width):
    """
    Calculate the south direction

    :param data:
    :param rows:
    :param cols:
    :param outdata:
    :param filter_width:
    """

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


def convo_nw(data, rows, cols, outdata, filter_width):
    """
    Calculate the north west direction

    :param data:
    :param rows:
    :param cols:
    :param outdata:
    :param filter_width:
    """

    ##    import pdb
    ##    pdb.set_trace()
    
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


def convo_ne(data, rows, cols, outdata, filter_width):
    """
    Calculate the north east direction

    :param data:
    :param rows:
    :param cols:
    :param outdata:
    :param filter_width:
    """

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


def convo_sw(data, rows, cols, outdata, filter_width):
    """
    Calculate the south west direction

    :param data:
    :param rows:
    :param cols:
    :param outdata:
    :param filter_width:
    """

    ##    import pdb
    ##    pdb.set_trace()
    
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


def convo_se(data, rows, cols, outdata, filter_width):
    """
    Calculate the south east direction

    :param data:
    :param rows:
    :param cols:
    :param outdata:
    :param filter_width:
    """

    ##    import pdb
    ##    pdb.set_trace()
    
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





##if __name__=='__main__':
##
##    # start timing
##    startTime = time.time()
##
##    root = 'N:\\climate_change\\workspaces\\Tina\Multiplier\\validation'
##
##    loc = 'act'
##    
##    terrain_convo(loc, root)
##
##    print 'finish successfully'
##
##    # figure out how long the script took to run
##    stopTime = time.time()
##    sec = stopTime - startTime
##    days = int(sec / 86400)
##    sec -= 86400*days
##    hrs = int(sec / 3600)
##    sec -= 3600*hrs
##    mins = int(sec / 60)
##    sec -= 60*mins
##    print 'The scipt took ', days, 'days, ', hrs, 'hours, ', mins, 'minutes ', '%.2f ' %sec, 'seconds'
##


