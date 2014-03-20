This package is used to produce wind terrain, shielding and topographic
multipliers.

Python 2.6, NumPy and SciPy are needed. ArcPy requiring ArcGIS 10
license is also needed.

The script for deriving terrain and shielding multipliers is
terr\_shield.py that consists of two modules: terrain and shielding.

Terrain module includes terrain\_class2mz\_orig.py and
direction\_filter.py. Shielding module includes dem\_slope\_aspect.py,
terrain\_class2ms\_orig.py, direction\_filter.py and combine.py.

Before running terr\_shield.py to produce terrain and shielding
multipliers, the configuration file named terr\_shield.cfg needs to be
configured. There are some variables to be pre-defined:

<strong>root:</strong> the working directory of the task. loc\_<br/>
<strong>list:</strong> the location of the interest.<br/>
<strong>cyclone\_area:</strong> if the location is within the cyclone area, it is yes, otherwise it is no.<br/>
<strong>ArcToolbox:</strong> the path of the ArcGIS tool box

Then copy the input files (dem and terrain classes) into the input
folder (created beforehand manually) under root, and start to run
terr\_shield.py. The resutls are respectively located under output
folder (created automatically during the process) under root.

This repository also includes Python code for evaluating the 2-D
topogrpahic multiplier.

The Python code was produced for the 2-D wind multipliers based on the
existing Octave code written by Chris Thomas (2009). To
maintainconsistency, the Python code was structured and functioned
closely to the Octave code. py\_north.py - the main code for calculating
2-D multipliers based on the input DEM and the wind direction (north).\
To adopt Chris Thomas (2009) modifications, the code does not rotate
matrices but extracts a line for that direction from the array holding
the DEM and operates on that line to produce the hill shape multipliers.
The calculated line of multipliers is then written back to the same
array that holds the DEM data. The smoothing is done upon output. In the
end, outputs including smoothed and unsmoothed data are written into
ascii files. It calls the following functions:<br/> 

ascii\_read.py \# read input DEM data<br/> 
make\_path.py \# generate indices of a data line depending on the direction <br/>
multiplier\_calc.py \# calculate the multipliers for a data line extracted from the dataset<br/>
multiplier\_calc.py needs to call two functions:<br/>
 Mh.py \# calculate Mh using the simpler formula modified by C.Thomas 2009<br/>
 findpeaks.py \# get the indices of the ridges in a data line Directory

structure:

../py-files/: store all the Python codes including main and functions.
../python\_output/: generated automatically to store output files.

Notes: Comparisons show small discrepancies between outputs from the
Python and the Octave codes. The difference varies depending on the wind
direction. The number of inconsistent data is up to 0.13% of the total
data (west wind) with the greatest magnitude of 0.02, which is 2% of the
minimum magnitude of output data. The discrepancies are believed due to
the inexact representation of decimal fractions in the IEEE floating
point standard and errors introduced when scaling by powers of ten.
Regardless of implementation language, similar problems would arise. It
also should be aware that some Python functions have slightly different
functionality. For example, for values exactly halfway between rounded
decimal values, Numpy rounds to the nearest even value.

V 0.2 - parallel implementation Ported to parallel execution - using
PyPar for MPI handling. To run in parallel mode: mpirun -np 8 python
topomult.py -i <input file> -o
<output path>






