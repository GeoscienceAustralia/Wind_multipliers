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
configured. There are two variables to be pre-defined:

    * **root:** the working directory of the task.
    * **upwind_length:** the upwind buffer distance

Then copy the input files (dem and terrain classes) into the input folder (created beforehand manually) under root, and start to run all_multipliers.py. The results are respectively located under output folder (created automatically during the process) under root directory.

This software implements parallelisation using PyPar for MPI handling. To run it in parallel mode, use  
mpirun -np ncpu python all_mulitpliers.py, while ncpu is the
number of CPUs adopted.

Improvements
==========

Version 2.0 has several improvements compared to Version 1.0:

	* Replaced the sub-processes with GDAL API, so some tiles are not missing on NCI.
	* Updated the tile output without overlapping areas.
	* Simplified the output structure.
	* Updated the terrain multiplier algorithm as per AS/NZS 1170.2 (2011) and recent amendments. 
	* Updated the topographic multiplier algorithm to include the Tasmania factor as per AS/NZS 1170.2 (2011).
	* Updated the topographic multiplier algorithm to remove the conservatism associated with the topographic multiplier as described in the document (*Yang, T., Nadimpalli, K. & Cechet, R.P. 2014. Local wind assessment in Australia: computation methodology for wind multipliers. Record 2014/33. Geoscience Australia, Canberra*) but with a modification (For topographic features such as shallow hills and escarpments where Mt < 1.4, a linear interpolation is constructed so that the percentage of reduction is gradually increased from 0 at point (Mt = 1) to 10 at point (Mt = 1.4))
	* Updated the shielding multiplier convolution mask by considering the Engineer's opinion.

Status 
====== 
.. image:: https://travis-ci.org/GeoscienceAustralia/Wind_multipliers.svg?branch=new0315
  :target: https://travis-ci.org/GeoscienceAustralia/Wind_multipliers 





