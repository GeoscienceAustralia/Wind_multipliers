The Wind Multiplier Computation Software 
=============================

This package is used to produce wind multipliers including terrain, shielding and topographic multipliers.

Dependencies 
=========
* `Python (2.7 preferred) <https://www.python.org/>`_, `Numpy <http://www.numpy.org/>`_, `Scipy <http://www.scipy.org/>`_, `GDAL <http://www.gdal.org/>`_, `netcdf4-python <https://code.google.com/p/netcdf4-python>`_; 
* For parallel execution, `Pypar <http://github.com/daleroberts/pypar>`_ is required; 

Usage
==== 

The script for deriving terrain, shielding and topographic multipliers is
all_multipliers.py that links four modules: terrain, shielding, topographic and utilities.

Before running all_multipliers.py to produce terrain, shielding and topographic
multipliers, the configuration file named multiplier_conf.cfg needs to be
configured. The following options need to be set in the configuration file:

    * **root:** the working directory of the task.
    * **upwind_length:** the upwind buffer distance
    * **terrain_data:** the location of the terrain dataset to be used 
    * **terrain_table:** the csv table outlining the format of the terrain dataset to be read in
    * **dem_data:** the location of the DEM dataset to be used

Start to run all_multipliers.py. The results are located under output folder (created automatically during the process) under root directory.

This software implements parallelisation using PyPar for MPI handling. To run it in parallel mode, use  
mpirun -np ncpu python all_mulitpliers.py, while ncpu is the
number of CPUs adopted.

terrain_table
-------------
The terrain table is a csv file that provides the 'key' for reading in the terrain dataset. The use of the terrain 
table means that any input landcover dataset can be used, with any classification method. 
The csv file requires the following headings:
    * CATEGORY: refers to the classification category used in the input terrain dataset
    * DESCRIPTION: of the classification category
    * ROUGHNESS_LENGTH_m: of the classification category
    
Change log (develop branch)
==========    
    * Terrain classification input dataset configuration is no longer hard-coded. (May 2017)

Status 
====== 
.. image:: https://travis-ci.org/GeoscienceAustralia/Wind_multipliers.svg?branch=new0315
  :target: https://travis-ci.org/GeoscienceAustralia/Wind_multipliers 





