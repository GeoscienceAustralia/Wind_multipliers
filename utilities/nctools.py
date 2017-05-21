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

from utilities.files import fl_program_version

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())
ISO_FORMAT = '%Y-%m-%d %H:%M:%S'


def clip_array(data, x_left, y_upper, pixelwidth, pixelheight, extent):

    """
    Return the clipped area of the input array according to an sub-extent

    :param data: :class:`numpy.ndarray` the input array
    :param x_left: `float` the left-most longitude vlaue
    :param y_upper: `float` the upper-most latitude values
    :param pixelwidth: `float` the pixel width
    :param pixelheight: `float` the pixel height
    :param extent: `tuple` the clipping extent

    :return: :class:`numpy.ndarray` the clipped array

    """
    LOGGER.debug("Clipping the array using extent: {0}".format(repr(extent)))

    lon_start = int(np.around((extent[0] - x_left)/pixelwidth))
    lat_start = int(np.around((-y_upper - extent[1])/pixelheight))

    cols = int(np.around((extent[2] - extent[0])/pixelwidth))
    rows = int(np.around((extent[1] - extent[3])/pixelheight))

    lon_end = lon_start + cols
    lat_end = lat_start + rows

    data_clip = data[lat_start:lat_end, lon_start:lon_end]

    return data_clip


def get_lat_lon(extent, pixelwidth, pixelheight):
    """
    Return the longitude and latitude values that lie within
    the given extent

    :param extent: `tuple` the clipping extent
    :param pixelwidth: `float` the pixel width
    :param pixelheight: `float` the pixel height

    :return: lon: :class:`numpy.ndarray` containing longitude values
    :return: lat: :class:`numpy.ndarray` containing latitude values

    """

    x_left = extent[0]
    y_upper = -extent[1]

    cols = int(np.around((extent[2] - extent[0])/pixelwidth))
    rows = int(np.around((extent[1] - extent[3])/pixelheight))

    lon = np.array(cols)
    lat = np.array(rows)

    lon = [x_left + 0.5 * pixelwidth + x * pixelwidth for x in range(0, cols)]
    lat = [-y_upper - 0.5 * pixelheight -
           y * pixelheight for y in range(0, rows)]

    return lon, lat


def nc_create_var(
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

    LOGGER.debug("Creating variable %s" % name)

    var = ncobj.createVariable(name, dtype, dimensions, **kwargs)

    if data:
        var[:] = np.array(data, dtype=dtype)

    if atts:
        var.setncatts(atts)

    return var


def nc_create_dim(ncobj, name, values, dtype, atts=None):
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
    var_dim = (name,)
    dimension = nc_create_var(ncobj, name, var_dim, dtype)
    dimension[:] = np.array(values, dtype=dtype)
    if atts:
        dimension.setncatts(atts)


def nc_save_grid(filename, dimensions, variables, nodata=-9999,
                 datatitle=None, gatts={}, writedata=True,
                 keepfileopen=False, zlib=True, complevel=4, lsd=None):

    """
    Save a gridded dataset to a netCDF file using NetCDF4.

    :param str filename: Full path to the file to write to.
    :param dimensions: :class:`dict`
        The input dict 'dimensions' has a strict structure, to
        permit insertion of multiple dimensions. The dimensions should be keyed
        with the slowest varying dimension as dimension 0.

        ::

            dimesions = {0:{'name':
                            'values':
                            'dtype':
                            'atts':{'long_name':
                                    'units':  ...} },
                         1:{'name':
                            'values':
                            'type':
                            'atts':{'long_name':
                                    'units':  ...} },
                                  ...}

    :param variables: :class:`dict`
        The input dict 'variables' similarly requires a strict structure:

        ::

            variables = {0:{'name':
                            'dims':
                            'values':
                            'dtype':
                            'atts':{'long_name':
                                    'units':
                                    ...} },
                         1:{'name':
                            'dims':
                            'values':
                            'dtype':
                            'atts':{'long_name':
                                    'units':
                                    ...} },
                             ...}

        The value for the 'dims' key must be a tuple that is a subset of
        the dimensions specified above.

    :param float nodata: Value to assign to missing data, default is -9999.
    :param str datatitle: Optional title to give the stored dataset.
    :param gatts: Optional dictionary of global attributes to include in the
                  file.
    :type gatts: `dict` or None
    :param dtype: The data type of the missing value. If not given, infer from
                  other input arguments.
    :type dtype: :class:`numpy.dtype`
    :param bool writedata: If true, then the function will write the provided
        data (passed in via the variables dict) to the file. Otherwise, no data
        is written.

    :param bool keepfileopen:  If True, return a netcdf object and keep the
        file open, so that data can be written by the calling program.
        Otherwise, flush data to disk and close the file.

    :param bool zlib: If true, compresses data in variables using gzip
        compression.

    :param integer complevel: Value between 1 and 9, describing level of
        compression desired. Ignored if zlib=False.

    :param integer lsd: Variable data will be truncated to this number of
        significant digits.

    :return: `netCDF4.Dataset` object (if keepfileopen=True)
    :rtype: :class:`netCDF4.Dataset`

    :raises KeyError: If input dimension or variable dicts do not have required
        keys.
    :raises IOError: If output file cannot be created.
    :raises ValueError: if there is a mismatch between dimensions and shape of
        values to write.

    """

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

        nc_create_dim(ncobj, d['name'], d['values'], d['dtype'], d['atts'])
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


def save_multiplier(multiplier_name, multiplier_values, lat, lon, nc_name):
    """
    Save multiplier data to a netCDF file.

    :param multiplier_name: `string` the multiplier name
    :param multiplier_values:  :class:`numpy.ndarray` the multiplier values
    :param lat: :class:`numpy.ndarray` containing latitude values
    :param lon: :class:`numpy.ndarray` containing longitude values
    :param nc_name: `string` the netcdf file name

    """
    cmd_folder = os.path.realpath(
        os.path.abspath(
            os.path.split(
                inspect.getfile(
                    inspect.currentframe()))[0]))
    par_folder = os.path.abspath(pjoin(cmd_folder, os.pardir))
    config = ConfigParser.RawConfigParser()
    config.read(pjoin(par_folder, 'multiplier_conf.cfg'))

    direction = os.path.splitext(nc_name)[0][-2:]

    if '_' in direction:
        direction = direction[-1:]

    multiplier = dict([('Mz', 'terrain multiplier'),
                       ('Ms', 'shielding multiplier'),
                       ('Mt', 'topographic multiplier')])

    terrain_map = config.get('inputValues', 'terrain_data')
    dem = config.get('inputValues', 'dem_data')

    global_atts = {'Abstract': ('This dataset is the local ' +
                                multiplier[multiplier_name] +
                                ' for each grid cell in ' + direction +
                                ' direction for this tile'),
                   'Lineage': ('Methodology is '
                               'based on the reference: Yang, T., Nadimpalli, '
                               'K. & Cechet, R.P. 2014. Local wind assessment '
                               'in Australia: computation methodology for wind'
                               ' multipliers. Record 2014/33. Geoscience '
                               'Australia, Canberra.'),
                   'Inputs': ('terrain data: {0}, dem data: {1}'
                              .format(str(terrain_map), str(dem))),
                   'Version': fl_program_version(),
                   'Python_ver': sys.version,
                   'Custodian': ('Geoscience Australia')}

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

    nc_save_grid(nc_name,
                 dimensions, variables,
                 nodata=-9999,
                 datatitle=multiplier_name + ' multiplier',
                 gatts=global_atts)
