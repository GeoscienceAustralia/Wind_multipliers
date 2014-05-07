import numpy

"""
.. module:: ascii_read.py
   :synopsis: Read input DEM stored in ../input

.. moduleauthor:: Daniel Wild <daniel.wild@ga.gov.au>


"""


class ElevationData(object):
    """
    Read input DEM stored in ../input

    :param input_dem: Input DEM as .asc file

    """
    def __init__(self, input_dem):

        with open(input_dem, 'r') as fid:
            for i in xrange(0, 6):
                line = fid.readline()
                contents = line.split()
                label = contents[0]
                setattr(self, label, float(contents[1]))

        self.data = numpy.genfromtxt(input_dem, skip_header=6)

        self.data = self.data.conj().transpose()

        numpy.putmask(self.data, self.data==self.NODATA_value, numpy.nan)

        # DEBUG - Uncomment to apply zero to NO_DATA values
        #numpy.putmask(self.data, self.data==self.NODATA_value, 0)
