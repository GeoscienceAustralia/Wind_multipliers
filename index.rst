.. WindMultipliers documentation master file, created by
   sphinx-quickstart on Wed Apr  2 10:27:30 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Wind Multipliers
**************************




     
Overview
===========================================


This package is used to produce wind terrain, shielding and topographic multipliers for national coverage using input of national dynamic land cover dataset v1 and 1 second SRTM level 2 derived digital eleveation models (DEM-S) version 1.0. The output is based on tiles with dimension about 1 by 1 decimal degree in netCDF format. It includes terrain, shielding and topographic multiplier respectively. Each multiplier further contains 8 directions. 



Dependencies
===========================================

Python 2.7, NumPy, SciPy, and GDAL are needed. 



Terrain, Shielding and Topographic Multipliers
==============================================

The script for deriving terrain, shielding and topographic multipliers is
**all_multipliers.py** that can be run in parallel using MPI. It links four modules: 

1. terrain; 
2. shielding;
3. topographic; and
4. utilities

terrain module includes: 

* terrain.py. 

shielding module includes:
 
* shielding.py.

topographic module includes:
 
* **topomult.py:**
* **make_path.py:** generate indices of a data line depending on the direction
* **multiplier_calc.py:** calculate the multipliers for a data line extracted from the dataset
* **multiplier_calc.py:** needs to call two functions:
	* Mh.py: calculate Mh 
	* findpeaks.py: get the indices of the ridges in a data line Directory

utilities module includes:
 
* _execute.py;
* blrb.py;
* files.py;
* get_pixel_size_grid.py;
* meta.py;
* nctools.py;
* value_lookup.py;
* vincenty.py.

.. note::
	Before running all_multipliers.py to produce terrain, 	shielding and topographic multipliers, the configuration 	file named multiplier_conf.cfg needs to be configured. There 	are some variables to be pre-defined:

	* **root:** the working directory of the task.
	* **upwind_length:** the upwind buffer distance

	Then copy the input files (dem and terrain classes) into the 	input folder (created beforehand manually) under root, and 	start to run all_multipliers.py. The resutls are 	respectively located under output folder (created 	automatically during 	the process) under root.


Background
===========================================


File Structure
===========================================


Notes
===========================================


Issues
======

Issues for this project are currently being tracked through JIRA here: http://intranet.ga.gov.au/jira/browse/WM


Code Documentation
==================

all_multipliers.py
===========================================

.. automodule:: all_multipliers
   :members:

.. toctree::
   :maxdepth: 2

   docs/topographic
   docs/terrain
   docs/shielding
   docs/utilities
   docs/tests_characterisation
   docs/tests
     

Module Index
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

