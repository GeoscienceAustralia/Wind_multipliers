"""
:mod:`makepath` -- Returns a vector of array indices for a path
===============================================================================

This module is called by the module :term:`topomult`
"""
import numpy


def make_path(nr, nc, n, dire):
    """
    Returns a vector of array indices for a path starting at index n in a
    matrix of size nr by nc and proceeding in direction dir, where dir is one
    of the 8 cardinal directions (n,s,e,w,ne,nw,se,sw).
    Note that the array indices are all 1-d indices.

    :param nr: `int` number of rows of the input DEM
    :param nc: `int` number of columns of the input DEM
    :param n: `int` starting index
    :param dire: `string` firection of the path

    :Returns: :class:`numpy.ndarray` the indices of a path
    """

    dire = dire.lower()

    # first compute the i,j coordinates from the 1-d index n
    i = numpy.mod(n, nr) + 1
    j = (n + 1 - i) / nr + 1

    # find the i and j increments according to
    # the directions in which we traverse

    if dire.find('n') >= 0:
        i_incr = 1
    elif dire.find('s') >= 0:
        i_incr = -1
    else:
        i_incr = 0

    if dire.find('w') >= 0:
        j_incr = 1
    elif dire.find('e') >= 0:
        j_incr = -1
    else:
        j_incr = 0

    # traverse, putting the positions in 1-index form
    result = []
    while ((i <= nr and i >= 1) and (j <= nc and j >= 1)):
        l = i + (j - 1) * nr - 1
        result.append(l)
        i += i_incr
        j += j_incr

    return result
