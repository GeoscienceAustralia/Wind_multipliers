# -*- coding: utf-8 -*-
"""
Created on Thu Jun 05 12:43:29 2014

@author: u89076
"""

import logging
from netCDF4 import Dataset
import numpy as np
import time
import getpass

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
ISO_FORMAT = '%Y-%m-%d %H:%M:%S'


def getLatLon(x_Left, y_Upper, pixelWidth, pixelHeight, cols, rows):    
    
    lon = np.array(cols)
    lat = np.array(rows)
    
    lon = [x_Left + 0.5*pixelWidth + x*pixelWidth for x in range(0, cols)]
    lat = [-y_Upper  - 0.5*pixelHeight - y*pixelHeight for y in range(0, rows)]  
    
    return lon, lat


def ncCreateVar(ncobj, name, dimensions, dtype, data=None, atts=None, **kwargs):    
    """    
    Create a `Variable` instance in a :class:`netCDF4.Dataset` or    
    :class:`netCDF4.Group` instance.    
    
    :param ncobj: :class:`netCDF4.Dataset` or :class:`netCDF4.Group` instance where the variable will be stored.    
    :type ncobj: :class:`netCDF4.Dataset` or :class:`netCDF4.Group`    
    :param str name: Name of the variable to be created.    
    :param tuple dimensions: dimension names that define the structure of the variable.    
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
    Create a `dimension` instance in a :class:`netcdf4.Dataset` or :class:`netcdf4.Group` instance.        
    
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
                                 
        if v.has_key('least_significant_digit'):            
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
    
    """  
    
#    import pdb
#    pdb.set_trace()
    
    
    dimensions = {    
        0: {                
            'name': 'lat',                
            'values': lat,                
            'dtype': 'd',                
            'atts': {                    
                'long_name': 'Latitude',                    
                'standard_name': 'latitude',                    
                'units': 'degrees_north',                    
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
                'long_name': multiplier_name + ' multiplier values for each grid', 
                'actual_range': (np.min(multiplier_values), np.max(multiplier_values)),                    
                'grid_mapping': 'GDA94'                
            }            
        }
    }


    ncSaveGrid(nc_name,                           
               dimensions, variables,                            
               nodata=-99,                           
               datatitle=multiplier_name + ' multiplier')       
        
                                          