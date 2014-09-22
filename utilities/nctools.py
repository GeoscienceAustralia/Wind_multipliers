"""
Tools used to produce output in netCDF format
"""

import sys
import logging
import os
from netCDF4 import Dataset
import numpy as np
import time
import getpass
import ConfigParser
from os.path import join as pjoin
import inspect

from utilities.files import flProgramVersion

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
ISO_FORMAT = '%Y-%m-%d %H:%M:%S'


def getLatLon(x_Left, y_Upper, pixelWidth, pixelHeight, cols, rows):
    """
    Return the longitude and latitude values that lie within
    the modelled domain

    :param x_Left: :class:`numpy.ndarray` containing longitude values
    :param y_Upper: :class:`numpy.ndarray` containing latitude values
    :param pixelWidth: :class:`numpy.ndarray` containing longitude values
    :param pixelHeightr: :class:`numpy.ndarray` containing latitude values
    :param cols: :class:`numpy.ndarray` containing longitude values
    :param rows: :class:`numpy.ndarray` containing latitude values

    :return: lon: :class:`numpy.ndarray` containing longitude values
    :return lat: :class:`numpy.ndarray` containing latitude values

    """
    lon = np.array(cols)
    lat = np.array(rows)

    lon = [x_Left + 0.5 * pixelWidth + x * pixelWidth for x in range(0, cols)]
    lat = [-
           y_Upper -
           0.5 *
           pixelHeight -
           y *
           pixelHeight for y in range(0, rows)]

    return lon, lat


def ncCreateVar(
        ncobj,
        name,
        dimensions,
        dtype,
        data=None,
        atts=None,
        **kwargs):
    """
    Create a `Variable` instance in a :class:`netCDF4.Dataset` or
    :class:`netCDF4.Group` instance.

    :param ncobj: :class:`netCDF4.Dataset` or :class:`netCDF4.Group` instance
                  where the variable will be stored.
    :type ncobj: :class:`netCDF4.Dataset` or :class:`netCDF4.Group`
    :param str name: Name of the variable to be created.
    :param tuple dimensions: dimension names that define the structure of
                             the variable.
    :param dtype: :class:`numpy.dtype` data type.
    :type dtype: :class:`numpy.dtype`
    :param data: :class:`numpy.ndarray` Array holding the data to be stored.
    :type data: :class:`numpy.ndarray` or None.
    :param dict atts: Dict of attributes to assign to the variable.
    :param kwargs: additional keyword args passed directly to the
                    :class:`netCDF4.Variable` constructor

    :return: :class:`netCDF4.Variable` instance
    :rtype: :class:`netCDF4.Variable`
    """

    logger.debug("Creating variable %s" % name)

    var = ncobj.createVariable(name, dtype, dimensions, **kwargs)

    if data:
        var[:] = np.array(data, dtype=dtype)

    if atts:
        var.setncatts(atts)

    return var


def ncCreateDim(ncobj, name, values, dtype, atts=None):
    """
    Create a `dimension` instance in a :class:`netcdf4.Dataset` or
    :class:`netcdf4.Group` instance.

    :param ncobj: :class:`netCDF4.Dataset` or :class:`netCDF4.Group` instance.
    :param str name: Name of the dimension.
    :param `numpy.ndarray` values: Dimension values.
    :param `numpy.dtype` dtype: Data type of the dimension.
    :param atts: Attributes to assign to the dimension instance
    :type atts: dict or None

    """

    ncobj.createDimension(name, np.size(values))
    varDim = (name,)
    dimension = ncCreateVar(ncobj, name, varDim, dtype)
    dimension[:] = np.array(values, dtype=dtype)
    if atts:
        dimension.setncatts(atts)


def ncSaveGrid(filename, dimensions, variables, nodata=-9999,
               datatitle=None, gatts={}, writedata=True,
               keepfileopen=False, zlib=True, complevel=4, lsd=None):

    #    import pdb
    #    pdb.set_trace()

    try:
        ncobj = Dataset(filename, 'w', format='NETCDF3_CLASSIC', clobber=True)
    except IOError:
        raise IOError("Cannot open {0} for writing".format(filename))

    # Dict keys required for dimensions and variables
    dimkeys = set(['name', 'values', 'dtype', 'atts'])
    varkeys = set(['name', 'values', 'dtype', 'dims', 'atts'])

    dims = ()
    for d in dimensions.itervalues():
        missingkeys = [x for x in dimkeys if x not in d.keys()]
        if len(missingkeys) > 0:
            ncobj.close()
            raise KeyError("Dimension dict missing key '{0}'".
                           format(missingkeys))

        ncCreateDim(ncobj, d['name'], d['values'], d['dtype'], d['atts'])
        dims = dims + (d['name'],)

    for v in variables.itervalues():
        missingkeys = [x for x in varkeys if x not in v.keys()]
        if len(missingkeys) > 0:
            ncobj.close()
            raise KeyError("Variable dict missing key '{0}'".
                           format(missingkeys))

        if v['values'] is not None:
            if (len(v['dims']) != v['values'].ndim):
                ncobj.close()
                raise ValueError("Mismatch between shape of "
                                 "variable and dimensions")

        if 'least_significant_digit' in v:
            varlsd = v['least_significant_digit']
        else:
            varlsd = lsd

        var = ncobj.createVariable(v['name'], v['dtype'],
                                   v['dims'],
                                   zlib=zlib,
                                   complevel=complevel,
                                   least_significant_digit=varlsd,
                                   fill_value=nodata)

        if (writedata and v['values'] is not None):
            var[:] = np.array(v['values'], dtype=v['dtype'])

        var.setncatts(v['atts'])

        # Additional global attributes:
        gatts['created_on'] = time.strftime(ISO_FORMAT, time.localtime())
        gatts['created_by'] = getpass.getuser()
        gatts['Conventions'] = 'CF-1.6'

        ncobj.setncatts(gatts)

        if datatitle:
            ncobj.setncattr('title', datatitle)

        if keepfileopen:
            return ncobj
        else:
            ncobj.close()
            return


def saveMultiplier(multiplier_name, multiplier_values, lat, lon, nc_name):
    """
    Save multiplier data to a netCDF file.

    :param multiplier_name: `string` the multiplier name
    :param multiplier_values:  :class:`numpy.ndarray` the multiplier values
    :param lat: :class:`numpy.ndarray` containing latitude values
    :param lon: :class:`numpy.ndarray` containing longitude values
    :param nc_name: `string` the netcdf file name

    """
#
#    import pdb
#    pdb.set_trace()

    direction = os.path.splitext(nc_name)[0][-2:]

    if '_' in direction:
        direction = direction[-1:]

    multiplier = dict([('Mz', 'terrain multiplier'),
                       ('Ms', 'shielding multiplier'),
                       ('Mt', 'topographic multiplier')])

    global_atts = {'Abstract': ('This dataset is the local ' +
                                multiplier[multiplier_name] +
                                ' for each grid cell in ' + direction +
                                ' direction for this tile'),
                   'Lineage': ('This dataset was produced based on the \
                               national dynamic land cover dataset v1 and \
                               1 second SRTM level 2 derived digtial \
                               models (DEM-S) version 1.0. Methodology is \
                               based on the reference: Yang, T., Nadimpalli, \
                               K. & Cechet, R.P. 2014. Local wind assessment \
                               in Australia: computation methodology for wind \
                               multipliers. Record 2014/33. Geoscience \
                               Australia, Canberra.'),
                   'Version': flProgramVersion(),
                   'Python_ver': sys.version,
                   'Custodian': ('Geoscience Australia')}

    cmd_folder = os.path.realpath(
        os.path.abspath(
            os.path.split(
                inspect.getfile(
                    inspect.currentframe()))[0]))
    par_folder = os.path.abspath(pjoin(cmd_folder, os.pardir))
    config = ConfigParser.RawConfigParser()
    config.read(pjoin(par_folder, 'multiplier_conf.cfg'))

    # Add configuration settings to global attributes:
#    for section in config.sections():
#        for option in config.options(section):
#            key = "{0}_{1}".format(section, option)
#            value = config.get(section, option)
#            global_atts[key] = value

    dimensions = {
        0: {
            'name': 'lat',
            'values': lat,
            'dtype': 'd',
            'atts': {
                'long_name': 'Latitude',
                'standard_name': 'latitude',
                'units': 'degrees_north',
                'actual_range': (np.min(lat), np.max(lat)),
                'axis': 'Y'
            }
        },
        1: {
            'name': 'lon',
            'values': lon,
            'dtype': 'd',
            'atts': {
                'long_name': 'Longitude',
                'standard_name': 'longitude',
                'units': 'degrees_east',
                'actual_range': (np.min(lon), np.max(lon)),
                'axis': 'X'
            }
        }
    }

    # Create variables:
    variables = {
        0: {
            'name': multiplier_name,
            'dims': ('lat', 'lon'),
            'values': multiplier_values,
            'dtype': 'f',
            'atts': {
                'long_name': multiplier_name +
                ' multiplier values for each grid',
                'actual_range': (np.nanmin(multiplier_values),
                                 np.nanmax(multiplier_values)),
                'grid_mapping': 'WGS-1984'
            }
        },
        1: {
            'name': 'crs',
            'dims': (),
            'values': None,
            'dtype': 'i',
            'atts': {
                'grid_mapping_name': 'latitude_longitude',
                'semi_major_axis': 6378137.0,
                'inverse_flattening': 298.257222101,
                'longitude_of_prime_meridian': 0.0
            }
        }
    }

    ncSaveGrid(nc_name,
               dimensions, variables,
               nodata=-9999,
               datatitle=multiplier_name + ' multiplier',
               gatts=global_atts)
