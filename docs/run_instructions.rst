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
        In order to update local wind multiplier dataset, the Land Cover Classification Scheme (LCCS) which is last updated for 2015 by Digital Earth Australia
        as a single-band GeoTiff with 25m spatial resolution, is collated to be used in 2021. This dataset is then overlaid with meshblock-derived dataset (2016) in the preprocessing stage
        for improving the categories with "Natural surface" types.
    * **Digital elevation model:** 
        The DEM dataset is used to calculate topography and shielding parameters. 
        The `1 second Shuttle Radar Topography Mission (SRTM) Smoothed Digital Elevation Models (DEM-S) Version 1.0 <http://www.ga.gov.au/metadata-gateway/metadata/record/gcat_72759>`_ is
        available to use as an input.
    * **Mesh blocks:**
        The administrative boundaries based on PSMA Australia or meshblock version 2016 is used for processing urban areas.
    * **Settlement types:**
        The settlement types based on 2016 census is sourced from Australian Bureau of Statistic (ABS) involved counting dwellings, place of Enumeration as well as UCL by STRD dwelling structure.
        This dataset is used for processing urban areas along with Meshblock input dataset in the pre-processing stage.    

All input datasets can be placed in the `input` folder within Wind_multipliers, however can be placed anywhere that can be accessed by the code.
The path to these datasets is set in the configuration file.
Previously, both landcover and DEM  datasets need to be in `.img` format, however this changed with the recent code releases. 

.. note:: The lowest resolution of the input Landcover and DEM datasets will determine the resolution of the calculated wind multipliers.     
    
Configuration file
==================
Before running all_multipliers.py to produce terrain, shielding and topographic multipliers, the configuration file `multiplier_conf.cfg`, in the
code home directory, needs to be configured for the preprocessing step. The following options need to be set in the configuration file:

    * **settlement_data** the location of the settlement types dataset to be used 
    * **settlement_cat** the category that defines the attribute in the settlement types for merge  
    * **land_use_data** the location of the meshblock dataset to be used 
    * **land_use_cat** the category that defines the attribute in the meshblock dataset for merge 
    * **crop_mask** the location of the layer for cropping the outcome of preprocessing step including vector and raster layers-set the parameter to None for continental coverage 
    * **input_topo** In order to map to the topographic file and takes the inputValues.dem_data, needs to be set to True. 
    * **topo_crop** Set this option to True for cropping the outcome of preprocessing step to the AOI set in **crop_mask** otherwise, default is False.

Running `pre_process.py` in pre_processing step will produce merged meshblock with settlment types as both vector and raster (i.e. shapefile and GeoTiff) layers. The second part of pre_processing step 
is to overlay merged meshblock raster layer with LCCCS dataset in order to improve the categories with "Natural surface" types. For this step, the areas with "Natural surface" types in LCCS dataset 
will be identified and their code will be replaced with the corresponding and approperiate code in the merged meshblock dataset using the `LCCS_meshblock_continent.py`. The output of this step 
is an updated LCCS layer that is going to be used as the **terrain_data** for producing multipliers. 

    * **root:** the working directory of the task.
    * **upwind_length:** the upwind buffer distance
    * **terrain_data:** the location of the terrain dataset to be used 
    * **terrain_table:** the location of the csv table outlining the format of the terrain dataset to be read in
    * **dem_data:** the location of the DEM dataset to be used

Assuming having the merged shapefile from the preporcess script, There is also one optional step between preprocessing and generating local wind multipliers using `rasterize.py`.
This step can be used to rasterise merged meshblock from shapefile to GeoTiff on a given topography file.There are two required arguments with `-i` and `-t` flags for shapefile and topography inputs.
Two other agruments are optional with `-a` and `-c` flags for attribute to rasterise and crop mask respectively. At the moment rasterise is based on CAT value set in the preprocess script.
If `-i` and `-t` are given, it will create the rasterised file (test.tiff) on the extend and resolution of the topography file (same projection). 
By adding the `-c` option, it will generate the same test.tiff but also two other files test_crop.tiff and [your topo filename]_crop.tiff being the cropped version of the files. It works with random shapes (not necessary rectangular one). 

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
The script for preprocessing mesh blocks and settlement types dataset is ``pre_process.py``. This script merges settlement and land use data using a common merging attribute.
To run ``pre_process.py`` type
``python pre_process.py -c multiplier_conf.cfg``
from the code home directory.

The script for rasterizing merged mesh block dataset is ``rasterize.py``. This script 
``python rasterize.py -c multiplier_conf.cfg -i <path to merged shapefile> -t <path to topography file>``

The script for deriving terrain, shielding and topographic multipliers is ``all_multipliers.py``. This script links four modules: terrain, shielding, 
topographic and utilities.
 
To run ``all_multipliers`` type 

``python all_multipliers.py -c multiplier_conf.cfg``

from the code home directory.

This software implements parallelisation using mpi4py for MPI handling. To run it in parallel mode, use

``mpirun -np ncpu python all_mulitpliers.py``

where ncpu is the number of CPUs adopted.

The results are located under output folder (created automatically during the process) under root directory.
