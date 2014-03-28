## --------------------------------------------------------
## Generate the indices of the valleys in a data line
## --------------------------------------------------------

import numpy
import findpeaks

def findvalleys(y):

    y = -y

    yud = numpy.flipud(y)
    yud = numpy.array(yud)
    ind = findpeaks.findpeaks(yud)
    ind = numpy.atleast_1d(ind)
    valley = numpy.size(y)-ind-1
    valley = numpy.flipud(valley)
    return valley
