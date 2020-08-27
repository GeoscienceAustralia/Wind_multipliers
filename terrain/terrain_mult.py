"""
:mod:`terrain` -- Calculate terrain multiplier
===============================================================================

This module is called by the module
:term:`all_multipliers` to calculate the terrain multiplier for an input tile
for 8 directions and output as NetCDF format.

:References:

    Yang, T., Nadimpalli, K. & Cechet, R.P. 2014. Local wind assessment
    in Australia: computation methodology for wind multipliers. Record 2014/33.
    Geoscience Australia, Canberra.

:moduleauthor: Tina Yang <tina.yang@ga.gov.au>

"""

# Import system & process modules
import os
import logging as log
from utilities import value_lookup
from utilities.nctools import save_multiplier, get_lat_lon, clip_array
from utilities.get_pixel_size_grid import get_pixel_size_grids
import numpy as np
from osgeo import gdal
from os.path import join as pjoin
import pandas as pd
import inspect
import configparser


def terrain(temp_tile, tile_extents_nobuffer):
    """
    Performs core calculations to derive the terrain multiplier

    :param temp_tile: `file` the image file of the input tile of the land cover
    :param tile_extents_nobuffer: `tuple` the input tile extent without buffer

    """

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
    x_left = geotransform[0]
    y_upper = -geotransform[3]
    pixelwidth = geotransform[1]
    pixelheight = -geotransform[5]

    # get the tile's longitude and latitude values used to save output in
    # netcdf
    lon, lat = get_lat_lon(tile_extents_nobuffer, pixelwidth, pixelheight)

    # get the average grid size in metre of the tile
    x_m_array, y_m_array = get_pixel_size_grids(temp_dataset)
    gridwidth = 0.5 * (np.mean(x_m_array) + np.mean(y_m_array))
    log.info('gridwidth is {0}'.format(gridwidth))

    # produce the original terrain multiplier from the input terrain map
    log.info(
        'Reclassify the terrain classes into initial terrain multipliers ...')
    band = temp_dataset.GetRasterBand(1)
    data = band.ReadAsArray(0, 0, cols, rows)

    nodata_value = band.GetNoDataValue()
    #if nodata_value is not None:
    #    data[np.where(data == nodata_value)] = np.nan
    #else:
    #    data[np.where(data is None)] = np.nan

    mz_init = get_terrain_table()
    reclassified_array = terrain_class2mz_orig(data, mz_init)

    # if the value is 0, it is nodata, if all 0s, empty tile
    if np.max(reclassified_array) == 0:
        log.info('Terrain dataset is all zeros. Terrain classification'
                 'will be skipped')
        return
    else:
        reclassified_array[reclassified_array == 0] = np.nan

    # assign nodata area as water with multiplier value 1
    mask = np.isnan(reclassified_array)
    reclassified_array[mask] = 1.0

    # convoulution of the original terrain multipler into different directions
    log.info('Moving average for each direction ...')
    dire = ['w', 'e', 'n', 's', 'nw', 'ne', 'se', 'sw']

    # set avearage and lag distance used for convolution as per
    # AS/NZ 1170.2 (2011) including amendments
    avg_dist = 500.
    lag_dist = 200.

    for one_dir in dire:
        log.info(one_dir)
        if one_dir in ['w', 'e', 'n', 's']:
            avg_width = int(np.around(avg_dist / gridwidth))
            lag_width = int(np.around(lag_dist / gridwidth))
        else:
            # for the diagonal directions, the avg_width is the same for x and
            # y component of the diagonal distance (avg_dist). lag_width is
            # the same principle as the avg_width
            avg_width = int(avg_dist / (gridwidth * 1.414))
            lag_width = int(lag_dist / (gridwidth * 1.414))

        # if the tile is smaller than the lag distance, no convolultion
        if lag_width > reclassified_array.shape[0]:
            outdata = reclassified_array
        else:
            # if the tile is smaller than the upwind buffer, all the tile is in
            # buffer
            if (avg_width + lag_width) > reclassified_array.shape[0]:
                avg_width = reclassified_array.shape[0] - lag_width

            log.info('convolution average width ' + str(avg_width))
            outdata = convo(one_dir, reclassified_array, avg_width, lag_width)
            outdata[mask] = np.nan

        # find output folder
        tile_folder = os.path.dirname(temp_tile)
        file_name = os.path.basename(temp_tile)

        # output format as netCDF4
        mz_folder = pjoin(tile_folder, 'terrain')

        tile_nc = pjoin(
            mz_folder,
            os.path.splitext(file_name)[0] +
            '_mz_' +
            one_dir +
            '.nc')
        log.info("Saving terrain multiplier in netCDF file")

        outdata_nobuffer = clip_array(outdata, x_left, y_upper, pixelwidth,
                                      pixelheight, tile_extents_nobuffer)

        save_multiplier('Mz', outdata_nobuffer, lat, lon, tile_nc)

        del outdata

    temp_dataset = None

    log.info(
        'finish terrain multiplier computation for this tile successfully')

def get_terrain_table():
    """
    Read in the terrain table specified in the config file

    :returns: pandas.DataFrame of the terrain classification data
    """
    cmd_folder = os.path.realpath(
        os.path.abspath(
            os.path.split(
                inspect.getfile(
                    inspect.currentframe()))[0]))
    par_folder = os.path.abspath(pjoin(cmd_folder, os.pardir))
    config = configparser.RawConfigParser()
    config.read(pjoin(par_folder, 'multiplier_conf.cfg'))

    log.info('Reading in the terrain table from the config file')
    terrain_table = config.get('inputValues', 'terrain_table')
    try:
        mz_init = pd.read_csv(terrain_table, comment='#', index_col=False)
    except IOError:
        log.exception("Terrain table file does not exist: {0}".format(terrain_table))
        import sys; sys.exit()
    except:
        raise
        
    
    return mz_init

def terrain_class2mz_orig(data, mz_init):
    """
    Transfer the landsat classified image into original terrain multiplier

    :param data: :class:`numpy.ndarray` the input terrain class values

    :returns: :class:`numpy.ndarray` the initial terrain multiplier value
    """
    outdata = np.zeros_like(data, np.float32)

    # Reclassify the land classes into initial terrain multipliers
    log.info('Calculating Mz for each terrain category')
    for ix, row in mz_init.iterrows():
        category = row['CATEGORY']
        roughness = row['ROUGHNESS_LENGTH_m']
        Mz = -0.2827 * np.log(0.4554*np.log(roughness) + 3.734) + 1.0762
        outdata[data == category] = Mz

    return outdata

def convo(one_dir, data, avg_width, lag_width):
    """
    Convolute the initial terrain multplier to final values for one of the
    eight directions

    :param one_dir: `str` the direction
    :param data: :class:`numpy.ndarray` the initial terrain multiplier values
    :param avg_width: :`int` the number of cells within the upwind buffer
    :param lag_width: :`int` the number of cells within the lag distance

    :returns: :class:`numpy.ndarray` the final terrain multiplier value
    """

    outdata = np.zeros_like(data, np.float32)
    rows = data.shape[0]
    cols = data.shape[1]

    for i in range(rows):
        for jj in range(cols):

            neighbour_sum = 0

            # find the total number of neighbours in this direction
            all_neighb_no = value_lookup.ALL_NEIGHB[one_dir](i, jj, rows, cols,
                                                             lag_width)

            if all_neighb_no > 0:
                if all_neighb_no < avg_width:
                    max_neighb_no = all_neighb_no
                else:
                    max_neighb_no = avg_width

                for m in range(max_neighb_no):

                    # get neighbour point location
                    point_row = value_lookup.POINT_R[one_dir](i, m, lag_width)
                    point_col = value_lookup.POINT_C[one_dir](jj, m, lag_width)

                    neighbour_sum += data[point_row, point_col]

                average = float(neighbour_sum) / float(max_neighb_no)
            else:
                average = data[i, jj]

            # get the calculated pixel value
            outdata[i, jj] = average
    return outdata
