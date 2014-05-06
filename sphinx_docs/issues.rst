

Known Issues
************

Issues are being tracked through JIRA, here: 


Confluence Page for JIRA Project: http://intranet.ga.gov.au/confluence/display/ICTSDCS/New+JIRA+Project+-+Wind+Multipliers




Topographic Mutliplier
===========================================


**Complex Value Casting Warning**

rhe-compute1 produces this warning when running topographic multiplier (warning was known prior to testing commencement)::

	/usr/local/python-2.7.2/lib/python2.7/site packages/scipy/signal/signaltools.py:             
	408: ComplexWarning: Casting complex values to real discards the imaginary part return sigtools._convolve2d(in1,in2,1,val,bval,fillvalue)


**OpenFabric/Infiniband (openib) Warning**

rhe-compute1 produces this error when using mpirun to run topomult. It appears to be linked to the initialisation of OpenFabric/Infiniband (openib) module.
Can stop openib from being loaded by including -mca btl ^openib when calling topomult.

Warning produced::

	librdmacm: couldn't read ABI version.
	librdmacm: assuming: 4
	CMA: unable to get RDMA device list
	CMA: unable to get RDMA device list
	--------------------------------------------------------------------------
	[[52708,1],2]: A high-performance Open MPI point-to-point messaging module
	was unable to find any relevant network interfaces:

	Module: OpenFabrics (openib)
  	Host: rhe-compute1.ga.gov.au

	Another transport will be used instead, although this may result in lower performance	

	...

	Pypar (version 2.1.4) initialised MPI OK with 8 processors
	[rhe-compute1.ga.gov.au:31350] 7 more processes have sent help message help-mpi- btl-base.txt / btl:no-nics
	[rhe-compute1.ga.gov.au:31350] Set MCA parameter "orte_base_help_aggregate" to 0 to see all help / error messages


**Null/NODATA Value Error**

The current version of topomult does not handle null/NODATA values (they will crash the program).
Previous versions of the topomult (namely the OCTAVE version) handled this by simply replacing any null values with the largest value in the data set.

This has been deemed insufficiently accurate, and further work should be done to find the most suitable approach.

Potential solutions currently include using 0 (the value for water), max value, or an average value. Ideally we would execute a manual calculation for a given data set, then test each of the potential solutions to find the most accurate.

Currently, to perform a test run of topomult with a data set containing NO_DATA values, we change the ``numpy.putmask`` value from ``numpy.nan`` to ``0``

around line 34 of ``ascii_read.py``::
	
	numpy.putmask(self.data, self.data==self.NODATA_value, 0)


**Extended Runtimes for Lat/Lon Data**

Currently investigating the extended runtimes produced by lat/lon data sets (e.g. SRTM tiles), as opposed to the projected eastings/northings data sets previously used.

Data sets of similar size are being processed in vastly different times, for example 10 hours vs 8 minutes for ~80MB tile.

Suspected that as code was written for x,y co-ordinates, it assumes this as input. It is currently not certain if the code is correctly handling Lat/Lon input.



