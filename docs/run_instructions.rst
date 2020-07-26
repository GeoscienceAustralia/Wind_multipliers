Instructions for running the wind multiplier code
*************************************************

Setting up the code repository
==============================
The Wind multipliers code is managed through `GitHub <https://github.com/GeoscienceAustralia/Wind_multipliers>`_. To get a copy of the code, either git
clone, or download the repository. To clone the repository using git (recommended), open up a command line window (e.g. cmd on Windows, or Terminal on
Mac), change to the directory where you would like the code to be installed, then type

`git clone https://github.com/GeoscienceAustralia/Wind_multipliers Wind_multipliers`

This will initialise a git repository called `Wind_multipliers` in the folder you are in. 

Dependencies 
============
* `Python (3.7 preferred) <https://www.python.org/>`_, `Numpy <http://www.numpy.org/>`_, `Scipy <http://www.scipy.org/>`_,
  `GDAL <http://www.gdal.org/>`_, `netcdf4-python <https://code.google.com/p/netcdf4-python>`_; 
* For parallel execution, `mpi4py <https://github.com/mpi4py/mpi4py>`_ is required;

In order for the code to run successfully, you will need to install a number of python packages. These are listed in the `requirements.txt` file in 
the code's home directory. To install these packages with pip, use:

`pip install -r requirements.txt`

Input datasets
==============
The wind multipliers code requires two input datasets:
    * **Landcover classification:** 
        The landcover classification dataset is used to calculate the change in wind speed over varying landcover surfaces.
        The input landcover classification dataset must be a classified dataset, broken into desired landcover categories, such as urban, forest, 
        grassland etc. The classification categories should be integer values (but this is not required). The interpretation of each landcover type is
        outlined in the accompanying terrain_table.
        The `National Dynamic Land Cover Dataset of Australia Version 2.0 <http://www.ga.gov.au/metadata-gateway/metadata/record/gcat_83868>`_ can be 
        used if a higher resolution dataset is not available.
    * **Digital elevation model:** 
        The DEM dataset is used to calculate topography and shielding parameters. 
        The `1 second Shuttle Radar Topography Mission (SRTM) Smoothed Digital Elevation Models (DEM-S) Version 1.0 <http://www.ga.gov.au/metadata-gateway/metadata/record/gcat_72759>`_ is
        available to use as an input.

Both input datasets can be placed in the `input` folder within Wind_multipliers, however can be placed anywhere that can be accessed by the code.
The path to these datasets is set in the configuration file.
At present, both datasets need to be in `.img` format, however this will be changed in future code releases. 

.. note:: The lowest resolution of the input Landcover and DEM datasets will determine the resolution of the calculated wind multipliers.     
    
Configuration file
==================
Before running all_multipliers.py to produce terrain, shielding and topographic multipliers, the configuration file `multiplier_conf.cfg`, in the
code home directory, needs to be configured. The following options need to be set in the configuration file:

    * **root:** the working directory of the task.
    * **upwind_length:** the upwind buffer distance
    * **terrain_data:** the location of the terrain dataset to be used 
    * **terrain_table:** the location of the csv table outlining the format of the terrain dataset to be read in
    * **dem_data:** the location of the DEM dataset to be used

terrain_table
-------------
The terrain table is a csv file that provides the 'key' for reading in the terrain dataset. The use of the terrain 
table means that any input landcover dataset can be used, with any classification method. 
The csv file requires the following headings:
    * **CATEGORY:** refers to the classification category used in the input terrain dataset
    * **DESCRIPTION:** of the classification category
    * **ROUGHNESS_LENGTH_m:** of the classification category
    * **SHIELDING:** parameter for urban land cover types. Other land cover types should be set to 1.0.

An example of the terrain table that would be used for the National Dynamic Landcover Dataset has been included in the code.

'''
CATEGORY,DESCRIPTION,ROUGHNESS_LENGTH_m,SHIELDING
1,'City buildings',2,0.85
2,'Forest',1,1
3,'High density (industrial) buildings',0.8,0.88
4,'Small town centres',0.4,0.9
5,'Suburban/wooded country',0.2,1
6,'Orchard, open forest',0.08,1
7,'Long grass with few trees',0.06,1
8,'Crops',0.04,1
9,'Open rough water, airfields, uncut grass etc.',0.02,1
10,'Cut grass',0.008,1
11,'Desert (stones),roads',0.006,1
12,'Mudflats/salt evaporators/sandy beaches',0.004,1
13,'Snow surface',0.002,1

# 'CATEGORY' refers to the classification category in the
# input terrain dataset. 
# 'DESCRIPTION' of the classification category
# 'ROUGHNESS_LENGTH_m' of the classification category
# 'SHIELDING' parameter for urban land cover types. Other land cover types should be set to 1.0.
# This example is taken from "AS/NZ Standarts 1170.2 -
# Structural design actions, Part 2: Wind Actions - 
# Supplement 1 (2002)"
'''

Running the code
================
The script for deriving terrain, shielding and topographic multipliers is ``all_multipliers.py``. This script links four modules: terrain, shielding, 
topographic and utilities.
 
To run ``all_multipliers`` type 

``python all_multipliers.py -c multiplier_conf.cfg``

from the code home directory.

This software implements parallelisation using mpi4py for MPI handling. To run it in parallel mode, use

``mpirun -np ncpu python all_mulitpliers.py``

where ncpu is the number of CPUs adopted.

The results are located under output folder (created automatically during the process) under root directory.


Merged files
============

*WIP: July 2020*

Two scripts in the `utilities` folder allow users to build merged files, which contain all directions as bands in the output file. 

`utilities/convert.py` reads a list of tile files and creates a single file, with the three components (Mz, Ms and Mt) combined (multiplied), and each direction stored as a separate band.

From the top-level output folder (specified in ``multiplier_conf.cfg`` as ``Output -- output_dir``), call ``utilities/convert.py``. 

Two additional output folders are created: ``M3`` and ``M3_max``. ``M3`` contains GeoTIFF files with eight bands, representing the merged multiplier data for each of the eight cardinal directions. ``M3__max`` folder contains GeoTIFF files that have a single band that is the maximum of all directions.

A virtual raster table file is added to the base output path, which enables seamless access to the tiles. 

Using command line GDAL::

    gdal_translate gdal_translate /<path>/wind-multipliers.vrt output.tif -projwin_srs EPSG:4326 -projwin 151.5 -28.5 153.5 -30.5

Using Python::

    gdal.UseExceptions()

    ds = gdal.Open('/<path>/wind-multipliers.vrt')
    gdal.Translate('output.tif', ds, projWin=[151.5, -28.5, 153.5, -30.5], options=gdal.TranslateOptions(gdal.ParseCommandLine("-co TILED=YES")))


