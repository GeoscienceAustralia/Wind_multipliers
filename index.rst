.. WindMultipliers documentation master file, created by
   sphinx-quickstart on Wed Apr  2 10:27:30 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Wind Multipliers
**************************
     
Overview
===========================================

This package is used to produce wind terrain, shielding and topographic multipliers for national coverage using a classified landcover dataset and a
DEM dataset. The default inputs to this code are the National Dynamic Land Cover Dataset of Australia Version 2.0 
(http://www.ga.gov.au/metadata-gateway/metadata/record/gcat_83868) and 1 second Shuttle Radar Topography Mission (SRTM) Smoothed Digital Elevation 
Models (DEM-S) Version 1.0 (http://www.ga.gov.au/metadata-gateway/metadata/record/gcat_72759). Both of these datasets are freely available to download.
Where possible, higher resolution datasets can be used to improve the resolution of the resulting wind multipliers. 

The output is based on tiles with dimension about 1 by 1 degree in netCDF format. It includes terrain, shielding and topographic multiplier 
respectively. Each multiplier further contains 8 directions. 


Dependencies
===========================================

Python 2.7, NumPy, SciPy, NetCDF4 and GDAL are needed. 


Package structures
==============================================

The script for deriving terrain, shielding and topographic multipliers is **all_multipliers.py** that can be run in parallel using MPI. It links 
four modules: 

1. terrain; 
2. shielding;
3. topographic; and
4. utilities

**Terrain** module includes: 

* **terrain_mult.py:** produce the terrain multiplier for a given tile 

**Shielding** module includes:
 
* **shield_mult.py:** produce the shielding multiplier for a given tile

**Topographic** module includes:
 
* **topo_mult.py:** produce the topographic multiplier for a given tile
    * make_path.py: generate indices of a data line depending on the direction    
    * multiplier_calc.py: calculate the multipliers for a data line extracted from the dataset:
        * mh.py: calculate Mh 
        * findpeaks.py: get the indices of the ridges in a data line Directory

**Utilities** module includes supporting tools such as:
 
* blrb.py;
* files.py;
* get_pixel_size_grid.py;
* meta.py;
* nctools.py;
* value_lookup.py;
* vincenty.py.


Background
===========================================

Wind multipliers are factors that transform regional wind speeds to local wind speeds considering local effects of land cover and topographic influences. It includes terrain, shielding, topographic and direction multipliers. Except the direction multiplier whose value can be defined specifically by the 
Australian wind loading standard AS/NZS 1170.2, terrain, shielding and topographic multipliers are calculated using this software package based on the principles and formulae defined in the AS/NZS 1170.2. The wind multipliers are primarily used for assessment of wind hazard at individual building locations.
Further details on wind multipliers can be found in Geoscience Australia record: *Local Wind Assessment in Australia: Computation Methodology for Wind Multipliers*, which is available via http://www.ga.gov.au/metadata-gateway/metadata/record/75299. 


Issues
======

Issues for this project are currently being tracked through Github.


Code Documentation
==================

.. toctree::
   :maxdepth: 2

   docs/run_instructions
   docs/all_multipliers
   docs/terrain
   docs/shielding
   docs/topographic
   docs/utilities
     

Module Index
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

