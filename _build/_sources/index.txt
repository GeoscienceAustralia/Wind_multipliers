.. WindMultipliers documentation master file, created by
   sphinx-quickstart on Wed Apr  2 10:27:30 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Wind Multipliers
**************************


     
Overview
===========================================


This package is used to produce wind terrain, shielding and topographic
multipliers.



Dependencies
===========================================

Python 2.6, NumPy and SciPy are needed. ArcPy requiring ArcGIS 10
license is also needed.



Terrain & Sheilding Multipliers
===========================================

The script for deriving terrain and shielding multipliers is
**terr_shield.py** that consists of two modules: 

1. terrain; and
2. shielding

Terrain module includes: 

* terrain_class2mz_orig.py; and
* direction_filter.py. 

Shielding module includes:
 
* dem_slope_aspect.py,
* terrain_class2ms_orig.py, 
* direction_filter.py,
* combine.py.

.. note::
	Before running terr_shield.py to produce terrain and 	shielding multipliers, the configuration file named 	terr_shield.cfg needs to be configured. There are some 	variables to be pre-defined:

	* **root:** the working directory of the task.
	* **loc_list:** the location of the interest.
	* **cyclone_area:** if the location is within the cyclone 	area, it is yes, otherwise it is no.
	* **ArcToolbox:** the path of the ArcGIS tool box

	Then copy the input files (dem and terrain classes) into the 	input folder (created beforehand manually) under root, and 	start to run terr_shield.py. The resutls are respectively 	located under output folder (created automatically during 	the process) under root.


Background
===========================================

This repository also includes Python code for evaluating the 2-D
topogrpahic multiplier.

The Python code was produced for the 2-D wind multipliers based on the existing Octave code written by Chris Thomas (2009). 

To maintainconsistency, the Python code was structured and functioned closely to the Octave code. 

py_north.py - the main code for calculating 2-D multipliers based on the input DEM and the wind direction (north). To adopt Chris Thomas (2009) modifications, the code does not rotate matrices but extracts a line for that direction from the array holding
the DEM and operates on that line to produce the hill shape multipliers.

The calculated line of multipliers is then written back to the same array that holds the DEM data. The smoothing is done upon output. 

In the end, outputs including smoothed and unsmoothed data are written into ascii files. It calls the following functions: 

* **ascii_read.py:** read input DEM data 
* **make_path.py:** generate indices of a data line depending on the direction
* **multiplier_calc.py:** calculate the multipliers for a data line extracted from the dataset
* **multiplier_calc.py:** needs to call two functions:
	* Mh.py: calculate Mh using the simpler formula modified by C.Thomas 2009
	* findpeaks.py: get the indices of the ridges in a data line Directory


File Structure
===========================================


* **py-files:** store all the Python codes including main and functions.
* **python_output:** generated automatically to store output files.


Notes
===========================================

Comparisons show small discrepancies between outputs from the
Python and the Octave codes. The difference varies depending on the wind direction. 

The number of inconsistent data is up to 0.13% of the total
data (west wind) with the greatest magnitude of 0.02, which is 2% of the minimum magnitude of output data. 

The discrepancies are believed due to the inexact representation of decimal fractions in the IEEE floating point standard and errors introduced when scaling by powers of ten. Regardless of implementation language, similar problems would arise. 

It also should be aware that some Python functions have slightly different functionality. For example, for values exactly halfway between rounded decimal values, Numpy rounds to the nearest even value.


Topographic Multiplier V 0.2
===========================================

Parallel implementation Ported to parallel execution - using
PyPar for MPI handling. 

To run in parallel mode:: 

$ mpirun -np 8 python topomult.py -i <input file> -o <output path>


.. note::
	Checking for infiniband may throw some warnings on rhe-compute1, eg::


		A high-performance Open MPI point-to-point messaging module was unable to find any relevant network interfaces

		Another transport will be used instead, although this may result in lower performance.
	
		librdmacm: couldn't read ABI version.
		librdmacm: assuming: 4
		CMA: unable to get RDMA device list 

	
	If not correctly running Infiniband etc. you can prevent it 	from being called by including::

	$ -mca btl ^openib

Issues
======

Issues for this project are currently being tracked through JIRA here: http://intranet.ga.gov.au/jira/browse/WM


Code Documentation
==================

.. toctree::
   :maxdepth: 2
   
   sphinx_docs/topographic
   sphinx_docs/terrain
   sphinx_docs/sheilding
   sphinx_docs/tests_characterisation
     

Module Index
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

