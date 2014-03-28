Documentation for Octave code for producing 2-D wind multipliers from digital elevation models

Useage

1. Requires that Octave be installed.

2. Requires the existence of 3 directories in the base directory, called respectively: m-files, input, output. The *.m files go in the m-files directory, the dem in the input directory, the output will be written to the output directory

3. Requires a dem in ESRI ascii format. The dem must be projected and have horizontal coordinates in metres. Put it (or a soft link to it) in the input directory. It must be called dem.asc (if you want to call it something else you can simply create a soft link called dem.asc that points to the dem you want to use.

4. The dem must not have any No Data values. Typically these might be water pixels, In which case you can simply set them to the value 0. The unix utility sed, for example, will accomplish this easily. In other cases the No Data values might arise near the boundary from projection of the dem, in which case you will need to clip it to a rectangular subregion. In some cases the dem might have No Data values arising from problems with the dem, in which case I suggest you get another one.  

5. To run it, go to the m-files directory and either type, for example, "north" at the Octave prompt, or type "octave north.m" at the linux shell prompt. Similarly for the other directions.

6. Alternatively, the script run_all.m will do all eight directions, one after the other. However the quickest way to get a large job done will be to run one direction on each of eight nodes of a linux cluster. Depending on domain size you may also be able to run more than one direction on each node.

Output

Produces 16 files, mh_dir.asc and mh_dir_smooth.asc where dir is one of n, s, e, w, ne, sw, nw, se. The smoothed files are computed using a 3 by 3 moving average smoother and give essentially identical results to those of Lin's Matlab code (see notes below). The unsmoothed files should not be used without first applying some form of smoothing. They are output in case the user determines that they wish to use a smoothing technique other than the default one supplied. 

Notes

The code is a modification of Matlab code produced for GA by X G Lin. It runs on Linux machines with Octave installed, and is far more memory efficient, though slower, than Lin's original code. It enables, for example, hillshape multipliers to be computed for all of Tasmania at 25 metre resolution, without tiling of the dem. It also enables jobs to be run on a linux cluster.

The code has been tested on various data sets and the mh_*_smoothed.asc files produced are (essentially) identical to the output files that are produced by Lin's matlab code. They are identical on the interior of the region. The only differences are at some points on the boundary, and these arise because Lin's code actually rotates the entire dem and pads (arbitrarily) with zeros to make it rectangular. Instead, the Octave code extracts lines from the dem and operates on these lines individually, so no zero padding is required. This is also the reason why the Octave code is more efficient in its use of memory, but slower in execution. In both cases (ie either using the original Lin version of the code or using this modified version of the code) the values computed near the boundary of the region should be ignored.

If necessary the Octave code will also run using Matlab, perhaps with minor modifications. This might be as simple as replacing endif with end.

C. Thomas
