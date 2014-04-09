#!/usr/bin/python2.6
##------------------------------------------------------
## Read input DEM stored in ../input 
##------------------------------------------------------
import numpy

"""
.. module:: test_topo
   :synopsis: Module used to initiate characterisation tests for topographic multiplier

.. moduleauthor:: Daniel Wild <daniel.wild@ga.gov.au>


"""


class ElevationData(object):


    def __init__(self, input_dem):
        """Test Class used to run a unit test comparison of expected against actual results outputted by topomult.py

    """
        with open(input_dem, 'r') as fid:
            for i in xrange(0, 6):
                line = fid.readline()
                contents = line.split()
                label = contents[0]
                setattr(self, label, float(contents[1]))

        self.data = numpy.genfromtxt(input_dem, skip_header=6)

        self.data = self.data.conj().transpose()
        numpy.putmask(self.data, self.data==self.NODATA_value, numpy.nan)
