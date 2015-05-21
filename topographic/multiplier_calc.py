"""
:mod:`multiplier_calc` -- Computes the topographic multipliers for a data line
===============================================================================

This module is called by the module :term:`topomult`
"""

import logging as log
import numpy as np
# calculate Mh using the simpler formula modified by C.Thomas 2009
import mh
# get the indices of the ridges in a data line
from findpeaks import findpeaks, findvalleys


def multiplier_calc(line, data_spacing):
    """
    Computes the multipliers for a data line

    :param line: :class:`numpy.ndarray` the elevation of a line
    :param data_spacing: `float` the distance between the neighour points

    :returns:  :class:`numpy.ndarray` the topographic values of the line
    """

    # --------------------------------------------------------
    # initialise m_array as an array filled with 1
    # --------------------------------------------------------

    nrow = np.size(line)
    m_array = np.ones((nrow, 1), dtype=float)

    # take the largest integer of each element of the data line
    fwd_line = np.floor(line)

    # Get the indices of the ridges & valleys
    ridge_ind = findpeaks(fwd_line)        # relative ind
    valley_ind = findvalleys(fwd_line)    # relative ind

    if np.size(ridge_ind) == 0:  # the DEM is completely flat
        log.debug("Flat line")

    # the DEM is downward slope all the time
    elif np.size(ridge_ind) == 1 and ridge_ind[0] == 0:
        log.debug("Downward slope")

    else:                      # 2 general cases, calculate m, works as Mh.m

        if ridge_ind[0] == 0:    # (1) down up down up ....
            for i in range(1, np.size(ridge_ind)):
                m = mh.mh_calc(fwd_line, ridge_ind[i], valley_ind[i - 1],
                               data_spacing)
                m_array = np.maximum(m_array, m)

        else:                    # (2) up dowm up dowm ....
            for i in range(0, np.size(ridge_ind)):
                m = mh.mh_calc(fwd_line, ridge_ind[i], valley_ind[i],
                               data_spacing)
                m_array = np.maximum(m_array, m)

    return m_array
