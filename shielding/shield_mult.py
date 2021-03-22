"""
:mod:`shielding` -- Calculate shielding multiplier
===============================================================================

This module is called by the module
:term:`all_multipliers` to calculate the shielding multiplier for an input tile
for 8 directions and output as NetCDF format.

:References:
    Yang, T., Nadimpalli, K. & Cechet, R.P. 2014. Local wind assessment
    in Australia: computation methodology for wind multipliers. Record 2014/33.
    Geoscience Australia, Canberra.

:moduleauthor: Tina Yang <tina.yang@ga.gov.au>

"""

# Import system & process modules
import sys
import os
import glob
import logging as log
import numexpr
from scipy import ndimage
from os.path import join as pjoin
import numpy as np
from osgeo.gdalconst import GDT_Float32
from osgeo import gdal

from utilities.config import configparser as config
from utilities import value_lookup
from utilities.get_pixel_size_grid import get_pixel_size_grids, \
                                          RADIANS_PER_DEGREE
from utilities.nctools import save_multiplier, get_lat_lon, clip_array

import pandas as pd


def shield(terrain, input_dem, tile_extents_nobuffer):
    """
    Performs core calculations to derive the shielding multiplier

    :param terrain: `file` the input tile of the terrain class map (landcover).
    :param input_dem: `file` the input tile of the DEM
    :param tile_extents_nobuffer: `tuple` the input tile extent without buffer

    """

    log.info('Derive slope and reclassified aspect ...   ')
    slope_array, aspect_array = get_slope_aspect(input_dem)

    log.info(
        'Reclassfy the terrain classes into initial shielding factors ...')
    ms_orig = terrain_class2ms_orig(terrain)

    log.info(
        'Moving average and combine slope and aspect for each direction ...')
    convo_combine(ms_orig, slope_array, aspect_array, tile_extents_nobuffer)

    del slope_array, aspect_array

    log.info(
        'finish shielding multiplier computation for this tile successfully')


def reclassify_aspect(data):
    """
    Reclassify the aspect valus from 0 ~ 360 to 1 ~ 9

    :param data: :class:`numpy.ndarray` the input aspect values 0 ~ 360

    :return: :class:`numpy.ndarray` the output aspect values 1 ~ 9
    """

    outdata = np.zeros_like(data, dtype=np.int)
    outdata.fill(9)

    outdata[np.where((data >= 0) & (data < 22.5))] = 1
    outdata[np.where((337.5 <= data) & (data <= 360))] = 1

    for i in range(2, 9):
        outdata[
            np.where((22.5 + (i - 2) * 45 <= data) &
                     (data < 67.5 + (i - 2) * 45))] = i

    return outdata


def get_slope_aspect(input_dem):
    """
    Calculate the slope and aspect from the input DEM

    :param input_dem: `file` the input DEM

    :return: :class:`numpy.ndarray` the output slope values
    :return: :class:`numpy.ndarray` the output aspect values
    """

    np.seterr(divide='ignore')

    if type(input_dem) == str:
        ds = gdal.Open(input_dem)
    else:
        ds = input_dem

    cols = ds.RasterXSize
    rows = ds.RasterYSize
    geotransform = ds.GetGeoTransform()
    pixel_x_size = abs(geotransform[1])
    pixel_y_size = abs(geotransform[5])
    band = ds.GetRasterBand(1)
    elevation_array = band.ReadAsArray(0, 0, cols, rows)
    elevation_array = elevation_array.astype(float)

    nodata_value = band.GetNoDataValue()
    if nodata_value is not None:
        elevation_array[np.where(elevation_array == nodata_value)] = np.nan
    else:
        elevation_array[np.where(elevation_array is None)] = np.nan

    mask = np.isnan(elevation_array)

    x_m_array, y_m_array = get_pixel_size_grids(ds)

    dzdx_array = ndimage.sobel(elevation_array, axis=1) / (8. * pixel_x_size)
    dzdx_array = numexpr.evaluate("dzdx_array * pixel_x_size / x_m_array")
    del x_m_array

    dzdy_array = ndimage.sobel(elevation_array, axis=0) / (8. * pixel_y_size)
    dzdy_array = numexpr.evaluate("dzdy_array * pixel_y_size / y_m_array")
    del y_m_array

    # Slope
    hypotenuse_array = np.hypot(dzdx_array, dzdy_array)
    slope_array = numexpr.evaluate(
        "arctan(hypotenuse_array) / RADIANS_PER_DEGREE")
    slope_array[mask] = np.nan
    del hypotenuse_array

    # Aspect
    # Convert angles from conventional radians to compass heading 0-360
    aspect_array = numexpr.evaluate(
        "(450 - arctan2(dzdy_array, -dzdx_array) / RADIANS_PER_DEGREE) % 360")
    # Derive reclassifed aspect...
    aspect_array_reclassify = reclassify_aspect(aspect_array)
    del aspect_array

    ds = None

    return slope_array, aspect_array_reclassify


def get_shielding_table():
    """
    Read in the terrain table specified in the config file

    :returns: pandas.DataFrame of the terrain classification data
    """
    log.info('Reading in the terrain table from the config file')
    terrain_table = config.get('inputValues', 'terrain_table')

    ms_init = pd.read_csv(terrain_table, comment='#', index_col=False)

    return ms_init


def terrain_class2ms_orig(terrain):
    """
    Reclassify the terrain classes into initial shielding factors

    :param terrain: `file` the input terrain class map

    :return: `file` the output initial shielding value
    """

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

    nodata_value = band.GetNoDataValue()
#    if nodata_value is not None:
#        data[np.where(data == nodata_value)] = np.nan
#    else:
#        data[np.where(data is None)] = np.nan
#
#    mask = np.isnan(data)

    if nodata_value is not None:
        data[np.where(data == nodata_value)] = -99
    else:
        data[np.where(data is None)] = -99

    mask = np.where(data == -99)

    ms_init = value_lookup.MS_INIT
    ms_init_new = get_shielding_table()
    outdata = np.ones_like(data, dtype=np.float32)

    for ix, row in ms_init_new.iterrows():
        category = row['CATEGORY']
        Ms = row['SHIELDING']
        outdata[data == category] = Ms / 100.
    # for i in [1, 3, 4, 5]:
    #     outdata[data == i] = ms_init[i] / 100.0

    outdata[mask] = np.nan

    ms_orig = pjoin(ms_folder, os.path.splitext(file_name)[0] + '_ms.img')
    ms_orig_ds = driver.Create(
        ms_orig,
        terrain_resample_ds.RasterXSize,
        terrain_resample_ds.RasterYSize,
        1,
        GDT_Float32)
    ms_orig_ds.SetGeoTransform(terrain_resample_ds.GetGeoTransform())
    ms_orig_ds.SetProjection(terrain_resample_ds.GetProjection())

    outband_ms_orig = ms_orig_ds.GetRasterBand(1)
    outband_ms_orig.WriteArray(outdata)
    del outdata

    # flush data to disk, set the NoData value and calculate stats
    outband_ms_orig.FlushCache()
    outband_ms_orig.SetNoDataValue(-99)
    outband_ms_orig.GetStatistics(0, 1)

    terrain_resample_ds = None

    return ms_orig


def convo_combine(ms_orig, slope_array, aspect_array, tile_extents_nobuffer):
    """
    Apply convolution to the orginal shielding factor for each direction and
    call the :term:`combine` module to consider the slope and aspect and remove
    conservitism to get final shielding multiplier values

    :param ms_orig: `file` the original shidelding factor map
    :param slope_array: :class:`numpy.ndarray` the input slope values
    :param aspect_array: :class:`numpy.ndarray` the input aspect values
    :param tile_extents_nobuffer: `tuple` the input tile extent without buffer

    """

    ms_orig_ds = gdal.Open(ms_orig)
    if ms_orig_ds is None:
        log.info('Could not open ' + ms_orig)
        sys.exit(1)

    log.info('ms_orig is {0}'.format(ms_orig))

    # get image size, format, projection
    cols = ms_orig_ds.RasterXSize
    rows = ms_orig_ds.RasterYSize
    geotransform = ms_orig_ds.GetGeoTransform()
    x_left = geotransform[0]
    y_upper = -geotransform[3]
    pixelwidth = geotransform[1]
    pixelheight = -geotransform[5]

    lon, lat = get_lat_lon(tile_extents_nobuffer, pixelwidth, pixelheight)

    band = ms_orig_ds.GetRasterBand(1)
    data = band.ReadAsArray(0, 0, cols, rows)

    if ms_orig_ds is None:
        log.info('Could not open {0}'.format(ms_orig))
        sys.exit(1)

    x_m_array, y_m_array = get_pixel_size_grids(ms_orig_ds)
    gridwidth = 0.5 * (np.mean(x_m_array) + np.mean(y_m_array))

    log.info('gridwidth is {0}'.format(gridwidth))

    ms_folder = os.path.dirname(ms_orig)
    file_name = os.path.basename(ms_orig)

    dire = ['w', 'e', 'n', 's', 'nw', 'ne', 'se', 'sw']

    for one_dir in dire:

        log.info(one_dir)

        kernel_size = int(100.0 / gridwidth)

        log.info('convolution kernel size is {0}'.format(str(kernel_size)))

        # if the resolution size is bigger than 100 m, no covolution just copy
        # the initial shielding factor to each direction
        if kernel_size > 0:
            outdata = np.zeros((rows, cols), np.float32)

            kern_dir = globals()['kern_' + one_dir]
            mask = kern_dir(kernel_size)
            outdata = blur_image(data, mask)
        else:
            outdata = data

        result = combine(outdata, slope_array, aspect_array, one_dir)
        log.debug('Maximum shielding value is {0}'.format(result.max()))
        log.debug('Minimum shielding value is {0}'.format(result.min()))
        del outdata

        # output format as netCDF4
        tile_nc = pjoin(
            ms_folder,
            os.path.splitext(file_name)[0] +
            '_' +
            one_dir +
            '.nc')
        log.info("Saving shielding multiplier in netCDF file")

        result_nobuffer = clip_array(result, x_left, y_upper, pixelwidth,
                                     pixelheight, tile_extents_nobuffer)

        save_multiplier('Ms', result_nobuffer, lat, lon, tile_nc)

        del result

    ms_orig_ds = None
    try:
        os.remove(ms_orig)
    except:
        pass
    os.chdir(ms_folder)
    filelist = glob.glob('*.xml')

    log.debug("useless xml files: {0}".format(repr(filelist)))

    if len(filelist) != 0:
        for f in filelist:
            try:
                os.remove(f)
            except OSError:
                pass


def combine(ms_orig_array, slope_array, aspect_array, one_dir):
    """
    Used for each direction to derive the shielding multipliers by considering
    slope and aspect after convolution in the previous step. It will also
    remove the conservatism.

    :param ms_orig_array: :class:`numpy.ndarray` convoluted shielding values
    :param slope_array: :class:`numpy.ndarray` the input slope values
    :param aspect_array_reclassify: :class:`numpy.ndarray` input aspect values
    :param one_dir: `str` the direction of wind

    :return: :class:`numpy.ndarray` the output shielding mutipler values
    """

    dire_aspect = value_lookup.DIRE_ASPECT
    aspect_value = dire_aspect[one_dir]

    conservatism = 0.9
    up_degree = 12.30
    low_degree = 3.27

    out_ms = ms_orig_array

    mask = np.isnan(out_ms)
    out_ms[mask] = -99

    slope_uplimit = np.where(
        (slope_array >= 12.30) & (
            aspect_array == aspect_value))
    slope_middle = np.where(
        (slope_array > 3.27) & (
            slope_array < 12.30) & (
            aspect_array == aspect_value))

    out_ms[slope_uplimit] = 1.0
    out_ms[slope_middle] = (
        (1.0 - ms_orig_array[slope_middle]) * (
            slope_array[slope_middle] - low_degree) / (
            up_degree - low_degree)) + ms_orig_array[slope_middle]

    ms_smaller = np.where(out_ms < conservatism)
    ms_bigger = np.where(out_ms >= conservatism)
    out_ms[ms_smaller] = out_ms[ms_smaller] * conservatism
    out_ms[ms_bigger] = out_ms[ms_bigger] ** 2

    out_ms[mask] = np.nan

    return out_ms


def init_kern_diag(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is south west direction

    :param size: `int` the buffer size of the convolution

    :return: :class:`numpy.ndarray` the output kernel used for convolution
    """
    kernel = np.zeros((2 * size + 1, 2 * size + 1))
    # kernel[size, size] = 1.0

    for i in range(1, size + 1):
        kernel[i - 1:size, size + i] = 1.0

    return kernel / kernel.sum()


def init_kern(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is north direction

    :param size: `int` the buffer size of the convolution

    :return: :class:`numpy.ndarray` the output kernel used for convolution
    """

    kernel = np.zeros((2 * size + 1, 2 * size + 1))

    # for i in range(0, size + 1):
    for i in range(1, size + 1):
        kernel[i + size, size] = 1.0
    for i in range(2, size + 1):
        kernel[size + i:, size - 1:size + 2] = 1.0

    return kernel / kernel.sum()


def kern_w(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is west direction

    :param size: `int` the buffer size of the convolution

    :return: :class:`numpy.ndarray` the output kernel used for convolution
    """

    return np.rot90(init_kern(size), 1)


def kern_e(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is east direction

    :param size: `int` the buffer size of the convolution

    :return: :class:`numpy.ndarray` the output kernel used for convolution
    """

    return np.rot90(init_kern(size), 3)


def kern_n(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is north direction

    :param size: `int` the buffer size of the convolution

    :return: :class:`numpy.ndarray` the output kernel used for convolution
    """

    return init_kern(size)


def kern_s(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is south direction

    :param size: `int` the buffer size of the convolution

    :return: :class:`numpy.ndarray` the output kernel used for convolution
    """

    return np.rot90(init_kern(size), 2)


def kern_ne(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is north-east direction

    :param size: `int` the buffer size of the convolution

    :return: :class:`numpy.ndarray` the output kernel used for convolution
    """

    return np.flipud(np.fliplr(init_kern_diag(size)))


def kern_nw(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is north-west direction

    :param size: `int` the buffer size of the convolution

    :return: :class:`numpy.ndarray` the output kernel used for convolution
    """

    return np.flipud(init_kern_diag(size))


def kern_sw(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is south-west direction

    :param size: `int` the buffer size of the convolution

    :return: :class:`numpy.ndarray` the output kernel used for convolution
    """

    return init_kern_diag(size)


def kern_se(size):
    """
    Returns a mean kernel for convolutions, with dimensions
    (2*size+1, 2*size+1), it is south-east direction

    :param size: `int` the buffer size of the convolution

    :return: :class:`numpy.ndarray` the output kernel used for convolution
    """

    return np.fliplr(init_kern_diag(size))


def blur_image(im, kernel, mode='constant'):
    """
    Blurs the image by convolving with a kernel (e.g. mean or gaussian) of
    typical size.

    :param im: :class:`numpy.ndarray` input data of initial shielding values
    :param kernel: :class:`numpy.ndarray` the kernel used for convolution

    :return: :class:`numpy.ndarray` the output data afer convolution
    """
    improc = ndimage.convolve(im, kernel, mode=mode, cval=1.0)
    return(improc)
