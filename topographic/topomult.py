"""
:mod:`topomult` -- Calculate topographic multiplier
===============================================================================

This module is called by the module
:term:`all_multipliers` to calculate the topographic multiplier for an input
tile for 8 directions and output as NetCDF format.

:References:
    Yang, T., Nadimpalli, K. & Cechet, R.P. 2014. Local wind assessment
    in Australia: computation methodology for wind multipliers. Record 2014/33.
    Geoscience Australia, Canberra.

:moduleauthor:
    Tina Yang <tina.yang@ga.gov.au>
    Histroical authors: Xunguo Lin, Chris Thomas, Wenping Jiang, Craig Arthur

"""

import os
from os.path import join as pjoin
import numpy as np
import math
import logging as log
from scipy import signal
from osgeo import gdal

from utilities.get_pixel_size_grid import get_pixel_size_grids
from utilities.nctools import save_multiplier, get_lat_lon, clip_array

import make_path
import multiplier_calc

__version__ = '1.0 - intergarate with terrian and shileding multiplier for \
               tiling and parallelisation'


def topomult(input_dem, tile_extents_nobuffer):
    """
    Executes core topographic multiplier functionality

    :param input_dem: `file` the input tile of the DEM
    """

    # find output folder
    mh_folder = pjoin(os.path.dirname(input_dem), 'topographic')
    file_name = os.path.basename(input_dem)
    #nc_folder = pjoin(mh_folder, 'netcdf')

    ds = gdal.Open(input_dem)
    nc = ds.RasterXSize
    nr = ds.RasterYSize

    geotransform = ds.GetGeoTransform()
    x_left = geotransform[0]
    y_upper = -geotransform[3]
    pixelwidth = geotransform[1]
    pixelheight = -geotransform[5]

    #lon, lat = get_lat_lon(x_left, y_upper, pixelwidth, pixelheight, nc, nr)
    lon, lat = get_lat_lon(tile_extents_nobuffer, pixelwidth, pixelheight)

    band = ds.GetRasterBand(1)
    elevation_array = band.ReadAsArray(0, 0, nc, nr)
    #elevation_array[np.where(elevation_array < -0.001)] = np.nan
    
    nodata_value = band.GetNoDataValue()
    if nodata_value is not None:
        elevation_array[np.where(elevation_array == nodata_value)] = np.nan
    else:
        elevation_array[np.where(elevation_array is None)] = np.nan

    elevation_array_tran = np.transpose(elevation_array)
    data = elevation_array_tran.flatten()

    x_m_array, y_m_array = get_pixel_size_grids(ds)
    cellsize = 0.5 * (np.mean(x_m_array) + np.mean(y_m_array))

    # Compute the starting positions along the boundaries depending on dir
    # Together, the direction and the starting position determines a line.
    # Note that the starting positions are defined
    # in terms of the 1-d index of the array.

    directions = ['n', 's', 'e', 'w', 'ne', 'nw', 'se', 'sw']

    for direction in directions:
        log.info(direction)

        if len(direction) == 2:
            data_spacing = cellsize * math.sqrt(2)
        else:
            data_spacing = cellsize

        mhdata = np.ones(data.shape)

        strt_idx = []
        if direction.find('n') >= 0:
            strt_idx = np.append(strt_idx, list(range(0, nr * nc, nr)))
        if direction.find('s') >= 0:
            strt_idx = np.append(strt_idx, list(range(nr - 1, nr * nc, nr)))
        if direction.find('e') >= 0:
            strt_idx = np.append(strt_idx, list(range((nc - 1) * nr, nr * nc)))
        if direction.find('w') >= 0:
            strt_idx = np.append(strt_idx, list(range(0, nr)))

        # For the diagonal directions the corner will have been counted twice
        # so get rid of the duplicates then loop over the data lines
        # (i.e. over the starting positions)
        strt_idx = np.unique(strt_idx)

        for ctr, idx in enumerate(strt_idx):
            log.debug('Processing path %3i' % ctr + ' of %3i' % len(strt_idx)
                      + ', index %5i.' % idx)

            # Get a line of the data
            # path is a 1-d vector which gives the indices of the data
            path = make_path.make_path(nr, nc, idx, direction)
            line = data[path]
            line[np.isnan(line)] = 0.
            m = multiplier_calc.multiplier_calc(line, data_spacing)

            # write the line back to the data array
            m = np.transpose(m)
            mhdata[path] = m[0, ].flatten()

        # Reshape the result to matrix like
        mhdata = np.reshape(mhdata, (nc, nr))
        mhdata = np.transpose(mhdata)
        
        # consider the Tasmania factor  
        if x_left > 143.0 and y_upper > 40.0:
            mhdata = tasmania(mhdata, elevation_array)               
        

        # smooth
        g = np.ones((3, 3)) / 9.
        mhsmooth = signal.convolve(mhdata, g, mode='same')
        mhsmooth[np.isnan(elevation_array)] = np.nan
        del mhdata

        # output format as netCDF4
        tile_nc = pjoin(mh_folder, os.path.splitext(file_name)[0][:-4] + '_mt_' 
                        + direction + '.nc')
                        
        mhsmooth_nobuffer = clip_array(mhsmooth, x_left, y_upper, pixelwidth, 
                                      pixelheight, tile_extents_nobuffer)
                                      
        save_multiplier('Mt', mhsmooth_nobuffer, lat, lon, tile_nc)
        del mhsmooth

        log.info('Finished direction {0}'.format(direction))

    ds = None


def tasmania(mh_in, dem):     
    mh_out = mh_in
    above_500m = np.where(dem > 500.0)
    mh_out[above_500m] = mh_in[above_500m]*(1.0 + 0.00015*dem[above_500m])

    return mh_out
        
