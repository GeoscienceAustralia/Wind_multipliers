import os, sys, time
import numpy as np
#from scipy import signal
import scipy.signal
import arcpy
from arcpy.sa import *
#import utils


def shielding_convo(loc, root):
    """
    apply convolution to the orginal shielding factor for each direction
    input: ms_orig.img
    outputs: shield_east.img, shield_west.img, ..., shield_sw.img etc.
    """

    arcpy.env.overwriteOutput = True
       
    work_folder = root + '\\process\\shielding'
    arcpy.env.workspace = work_folder
    
    input_img = loc + '_ms_orig'
    
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
    lowleft_corner = arcpy.Point(ds.extent.XMin, ds.extent.YMin)
    print 'lower left X,Y: ', lowleft_corner
    print 'resolution ', pixelWidth, 'x', pixelHeight

    # get georeference info
    sr = ds.spatialReference

    
    data = arcpy.RasterToNumPyArray(ds)

    
    dire = ['w', 'e', 'n', 's', 'nw', 'ne', 'se', 'sw']

    #dire = ['w']

    for one_dir in dire:

        print one_dir
        output_dir = loc + '_shield_' + one_dir + '.img'

        if one_dir in ['w', 'e', 'n', 's']:
            kernel_size = int(100/pixelWidth) - 1
        else:
            kernel_size = int(100/pixelWidth)
            
        print 'convolution kernel size ' + str(kernel_size) 
        
        # if the resolution size is bigger than 100 m, no covolution just copy the initial shielding factor to each direction
        if kernel_size > 0: 
            outdata = np.zeros((rows, cols), np.float32)
    
            kern_dir = globals()['kern_' + one_dir]
            mask = kern_dir(kernel_size)
            outdata = blur_image(data, mask)
    
            if arcpy.Exists(output_dir):
                arcpy.Delete_management(output_dir)
    
            arcpy.NumPyArrayToRaster(outdata, lowleft_corner, pixelWidth, pixelHeight).save(output_dir)        
            arcpy.DefineProjection_management(output_dir, sr)
    
            del outdata            
        else:             
            arcpy.CopyRaster_management(input_img, output_dir)


    ds = None
    del data
   

    


def init_kern_diag(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is north east direction
    """
    kernel = np.zeros((2*size+1, 2*size+1))
    kernel[size, size] = 1.0
    kernel[size-3:size, size+1] = 1.0
    kernel[size-2:size, size+2] = 1.0
    kernel[size-1, size+3] = 1.0    
    
    return kernel / kernel.sum()


def init_kern(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is south direction
    """
    kernel = np.zeros((2*size+1, 2*size+1))
    kernel[size+2:, size-1:size+2] = 1.0
    kernel[size:size+2, size] = 1.0    
    
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


def blur_image(im, kernel, mode='valid'):
    """
    Blurs the image by convolving with a kernel (e.g. mean or gaussian) of typical
    size n. The optional keyword argument ny allows for a different size in the
    y direction.
    """    
    improc = scipy.signal.convolve(im, kernel, mode=mode)
    return(improc)


if __name__=='__main__':
    
    # start timing
    startTime = time.time()

    # set directory
    #os.chdir(r'N:\climate_change\workspaces\Tina\Multiplier\bushfire\output\shielding')

    root = r'N:\climate_change\CHARS\B_Wind\Projects\Multipliers\test_data\hobart'
                             
    loc = 'hoba'
    
    shielding_convo(loc, root)

    print 'finish successfully'

    # figure out how long the script took to run
    stopTime = time.time()
    sec = stopTime - startTime
    days = int(sec / 86400)
    sec -= 86400*days
    hrs = int(sec / 3600)
    sec -= 3600*hrs
    mins = int(sec / 60)
    sec -= 60*mins
    print 'The scipt took ', days, 'days, ', hrs, 'hours, ', mins, 'minutes ', '%.2f ' %sec, 'seconds'

