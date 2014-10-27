"""
:mod:`get_pixel_size_grid` -- calculate the image pixel size in meter
===============================================================================

:moduleauthor: Alex Ip

"""

import numpy as np
import logging as log
from osgeo import osr

from utilities.vincenty import vinc_dist
from utilities.blrb import interpolate_grid


RADIANS_PER_DEGREE = 0.01745329251994329576923690768489


class Earth(object):

    """
    Values relevant to earth.

    """

    # Mean radius
    RADIUS = 6371009.0  # (metres)

    # WGS-84
    # RADIUS = 6378135.0  # equatorial (metres)
    # RADIUS = 6356752.0  # polar (metres)

    # Length of Earth ellipsoid semi-major axis (metres)
    SEMI_MAJOR_AXIS = 6378137.0

    # WGS-84
    A = 6378137.0           # equatorial radius (metres)
    B = 6356752.3142        # polar radius (metres)
    F = (A - B) / A         # flattening
    ECC2 = 1.0 - B ** 2 / A ** 2  # squared eccentricity

    MEAN_RADIUS = (A * 2 + B) / 3

    # Earth ellipsoid eccentricity (dimensionless)
    # ECCENTRICITY = 0.00669438
    # ECC2 = math.pow(ECCENTRICITY, 2)

    # Earth rotational angular velocity (radians/sec)
    OMEGA = 0.000072722052


def get_pixel_size(dataset, xxx_todo_changeme):
    """
    Returns X & Y sizes in metres of specified pixel as a tuple.
    N.B: Pixel ordinates are zero-based from top left

    :param dataset: `file` the input dataset
    :param xxx_todo_changeme: `tuple` the input (x, y) point

    :return: tuple of `float` the grid size at the input (x, y) point
    """
    (x, y) = xxx_todo_changeme
    log.debug('(x, y) = (%f, %f)', x, y)

    spatial_reference = osr.SpatialReference()
    spatial_reference.ImportFromWkt(dataset.GetProjection())

    geotransform = dataset.GetGeoTransform()
    log.debug('geotransform = %s', geotransform)

    latlong_spatial_reference = spatial_reference.CloneGeogCS()
    coord_transform_to_latlong = \
        osr.CoordinateTransformation(spatial_reference,
                                     latlong_spatial_reference)

    # Determine pixel centre and edges in georeferenced coordinates
    xw = geotransform[0] + x * geotransform[1]
    yn = geotransform[3] + y * geotransform[5]
    xc = geotransform[0] + (x + 0.5) * geotransform[1]
    yc = geotransform[3] + (y + 0.5) * geotransform[5]
    xe = geotransform[0] + (x + 1.0) * geotransform[1]
    ys = geotransform[3] + (y + 1.0) * geotransform[5]

    log.debug('xw = %f, yn = %f, xc = %f, yc = %f, xe = %f, ys = %f',
              xw, yn, xc, yc, xe, ys)

    # Convert georeferenced coordinates to lat/lon for Vincenty
    lon1, lat1, _z = coord_transform_to_latlong.TransformPoint(xw, yc, 0)
    lon2, lat2, _z = coord_transform_to_latlong.TransformPoint(xe, yc, 0)
    log.debug('For X size: (lon1, lat1) = (%f, %f), (lon2, lat2) = (%f, %f)',
              lon1, lat1, lon2, lat2)
    x_size, _az_to, _az_from = vinc_dist(Earth.F, Earth.A,
                                         lat1 * RADIANS_PER_DEGREE,
                                         lon1 * RADIANS_PER_DEGREE,
                                         lat2 * RADIANS_PER_DEGREE,
                                         lon2 * RADIANS_PER_DEGREE)

    lon1, lat1, _z = coord_transform_to_latlong.TransformPoint(xc, yn, 0)
    lon2, lat2, _z = coord_transform_to_latlong.TransformPoint(xc, ys, 0)
    log.debug('For Y size: (lon1, lat1) = (%f, %f), (lon2, lat2) = (%f, %f)',
              lon1, lat1, lon2, lat2)
    y_size, _az_to, _az_from = vinc_dist(Earth.F, Earth.A,
                                         lat1 * RADIANS_PER_DEGREE,
                                         lon1 * RADIANS_PER_DEGREE,
                                         lat2 * RADIANS_PER_DEGREE,
                                         lon2 * RADIANS_PER_DEGREE)

    log.debug('(x_size, y_size) = (%f, %f)', x_size, y_size)
    return (x_size, y_size)


def get_pixel_size_grids(dataset):
    """
    Returns two grids with interpolated X and Y pixel sizes for given datasets

    :param dataset: `file` the input dataset

    :return: tuple of :class:`numpy.ndarray` grid sizes for input dataset
    """

#    import pdb
#    pdb.set_trace()

    def get_pixel_x_size(x, y):
        return get_pixel_size(dataset, (x, y))[0]

    def get_pixel_y_size(x, y):
        return get_pixel_size(dataset, (x, y))[1]

    x_size_grid = np.zeros((dataset.RasterYSize,
                            dataset.RasterXSize)).astype(np.float32)
    interpolate_grid(depth=1, shape=x_size_grid.shape,
                     eval_func=get_pixel_x_size, grid=x_size_grid)

    y_size_grid = np.zeros((dataset.RasterYSize,
                            dataset.RasterXSize)).astype(np.float32)
    interpolate_grid(depth=1, shape=y_size_grid.shape,
                     eval_func=get_pixel_y_size, grid=y_size_grid)

    return (x_size_grid, y_size_grid)
