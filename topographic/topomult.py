import os
from os.path import join as pjoin, exists
import numpy as np
import math
import logging as log
import itertools
import ConfigParser
from scipy import signal

from ascii_read import ElevationData
import make_path       
import multiplier_calc 

from files import flStartLog

__version__ = '0.4 - intergarate with terrian ans shileding multiplier for tiling and parallelisation'


def topomult(input_dem):

    """
    Executes core topographic multiplier functionality

    :param input_dem: The path for input DEM

    """
    directions = ['n','s','e','w','ne','nw','se','sw']
   
   # find output folder
    mt_folder = pjoin(os.path.dirname(input_dem), 'topographic')
    file_name = os.path.basename(input_dem) 
    
    # read input data using ascii_read. Note: data was flattened to a 
    # single array
    log.info('Reading data from {0}'.format(input_dem))
    
    DEM = ElevationData(input_dem)
    
    
    
    nr = int(DEM.nrows)
    nc = int(DEM.ncols)
    xll = DEM.xllcorner
    yll = DEM.yllcorner
    cellsize = DEM.cellsize
    
    import pdb
    pdb.set_trace()
    
    data =  DEM.data.flatten()
    
    log.info('xll = %f' % xll)
    log.info('yll = %f' % yll)
    log.info('data_spacing = %f' % cellsize)
    
    # Compute the starting positions along the boundaries depending on dir 
    # Together, the direction and the starting position determines a line.
    # Note that the starting positions are defined
    # in terms of the 1-d index of the array.
    
    if len(direction) == 2:
        data_spacing = DEM.cellsize*math.sqrt(2)
    else:
        data_spacing = DEM.cellsize
        
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
        M = M.conj().transpose()
        Mhdata[path] = M[0,].flatten()
    
    # Reshape the result to matrix like 
    Mhdata = np.reshape(Mhdata, (nc, nr))
    Mhdata = Mhdata.conj().transpose()
    
    # Output unsmoothed data to an ascii file
    ofn = pjoin(mh_data_dir, 'mh_'+ direction + '.asc')
    log.info( 'outputting unsmoothed data to: %s' % ofn )
    
    fid = open(ofn, 'w')
    
    fid.write('ncols         '+str(nc)+'\n')
    fid.write('nrows         '+str(nr)+'\n')
    fid.write('xllcorner     '+str(xll)+'\n')
    fid.write('yllcorner     '+str(yll)+'\n')
    fid.write('cellsize       '+str(cellsize)+'\n')
    fid.write('NOdata_struct_value  -9999\n')
    
    np.savetxt(fid, Mhdata, fmt ='%4.2f', delimiter = ' ', newline = '\n') 
    
    # Output smoothed data to an ascii file
    ofn = pjoin(mh_data_dir, 'mh_'+ direction + '_smooth.asc')
    log.info( 'outputting smoothed data to: %s' % ofn )
     
    fid = open(ofn,'w')
    fid.write('ncols         '+str(nc)+'\n')
    fid.write('nrows         '+str(nr)+'\n')
    fid.write('xllcorner     '+str(xll)+'\n')
    fid.write('yllcorner     '+str(yll)+'\n')
    fid.write('cellsize       '+str(cellsize)+'\n')
    fid.write('NOdata_struct_value  -9999\n')
    
    g = np.ones((3, 3))/9.
    
    mhsmooth = signal.convolve2d(Mhdata, g, mode='same', boundary='fill', 
                                 fillvalue=1)
   
    np.savetxt(fid, mhsmooth, fmt ='%4.2f', delimiter = ' ', newline = '\n') 
    
    fid.close()
    
    log.info('Finished direction %s' % direction)

   
if __name__ == '__main__': 
    #dem = '/nas/gemd/climate_change/CHARS/B_Wind/Projects/Multipliers/validation/output_work/test_dem.img'
    dem = r'N:\climate_change\CHARS\B_Wind\Projects\Multipliers\validation\output_work\dem.asc'
    topomult(dem)
