This package is used to produce wind terrain, shielding and topographic
multipliers.

Python 2.7, NumPy, SciPy and GDAL are needed. 

The script for deriving terrain, shielding and topographic multipliers is
all_multipliers.py that links three modules: terrain, shielding and topographic.

Before running all_multipliers.py to produce terrain, shielding and topographic
multipliers, the configuration file named multiplier_conf.cfg needs to be
configured. There are some variables to be pre-defined:

    * **root:** the working directory of the task.
    * **upwind_length:** the upwind buffer distance

Then copy the input files (dem and terrain classes) into the input
folder (created beforehand manually) under root, and start to run
all_multipliers.py. The resutls are respectively located under output
folder (created automatically during the process) under root.

This version is parallel implementation using PyPar for MPI handling. To run it
in parallel mode: mpirun -np ncpu python all_mulitpliers.py, while ncpu is the
number of CPUs adopted.





