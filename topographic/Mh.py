"""
:mod:`mh` -- Calculate the topographic multipliers
===============================================================================

This module is called by the module :term:`multiplier_calc`
"""

import numpy as np


def escarpment_factor(profile, ridge, valley, data_spacing):
    """
    Calculate escarpment factor

    :param profile: :class:`numpy.ndarray` the elevation of a line
    :param ridge: :class:`numpy.ndarray` the indices of the ridges of a line
    :param valley: :class:`numpy.ndarray` the indices of the valleys of a line
    :param data_spacing: `float` distance between neighbour points of a line

    :return: `float` the escarpment factor
    """

    max_escarp = 3
    min_escarp = 0.5
    nrow = np.size(profile)

    h = profile[ridge] - profile[valley]
    lu = abs(ridge - valley) * data_spacing / 2
    slope = h / (2 * lu)
    beta_ind = np.minimum(nrow - 1, np.floor(ridge + (2 * lu / data_spacing)))
    h_r2beta = profile[ridge] - profile[beta_ind]
    d_r2beta = (beta_ind - ridge) * data_spacing
    if d_r2beta > 0:                 # d_r2beta can be 0, 25, 50, ...
        slope_r2ml2 = h_r2beta / d_r2beta

        # when a symmetrical ridge slope_r2ml2=slope so escarp_factor=1
        # If slope_r2ml2=0, escarp_factor=2.5
        escarp_factor = 2.5 - 1.5 * slope_r2ml2 / slope

        if escarp_factor < min_escarp:
            escarp_factor = min_escarp
        elif escarp_factor > max_escarp:
            escarp_factor = max_escarp

    else:      # the ridge is on the end
        slope_r2ml2 = 999
        escarp_factor = 1

    return escarp_factor


def mh_calc(profile, ridge, valley, data_spacing):
    """
    Calculate topographic multiplier

    :param profile: :class:`numpy.ndarray` the elevation of a line
    :param ridge: :class:`numpy.ndarray` the indices of the ridges of a line
    :param valley: :class:`numpy.ndarray` the indices of the valleys of a line
    :param data_spacing: `float` distance between neighbour points of a line

    :return: :class:`numpy.ndarray` the topogrpahic multiplier of the line
    """

    # --------------------------------------------------------
    # initialise parameters
    # --------------------------------------------------------

    h_threshold = 10     # height threshold for mh calculation
    lu_threshold = data_spacing    # half distance threshold for mh calculation

    z = 10  # building height
    nrow = np.size(profile)
    m = np.ones((nrow, 1), dtype=float)

    h = profile[ridge] - profile[valley]
    lu = abs(ridge - valley) * data_spacing / 2
    slope = h / (2 * lu)
    l1_capital = np.maximum(0.36 * lu, 0.4 * h)
    l2_capital = 4 * l1_capital

    escarp_factor = escarpment_factor(profile, ridge, valley, data_spacing)
    fl2_ind = np.maximum(0, ridge - np.floor(l2_capital / data_spacing))
    if slope < 0.05 or h < h_threshold or lu < lu_threshold:
        return m

    # calculate the mh from the front l2_capital to the back l2_capital with 
    # the escarpment factor considered:
    l1 = int(np.floor(fl2_ind)) - 1
    l2 = int(
        np.floor(
            np.minimum(
                nrow -
                1,
                ridge +
                np.floor(
                    escarp_factor *
                    l2_capital /
                    data_spacing)) +
            1))

    for k in range(l1, l2):
        x = (ridge - k) * data_spacing

        # within the region of l2_capital up to the ridge
        if x >= 0 and x < l2_capital:
            m[k] = 1 + (h / (3.5 * (z + l1_capital))) * (1 - abs(x) / 
                                                             l2_capital)

            # --------------------------------------------------------
            # for larger slopes, you still use the formula to calculate M,
            # then re-value to 1.71 when it is larger. If use 1.71 for any
            # slope greater than 0.45, then all the points within the 
            # l2_capital zone will have 1.71 rather than a gradual increasing, 
            # peaks and decreasing pattern.
            # --------------------------------------------------------

            if m[k] > 1.71:
                m[k] = 1.71

        # more or less a symmetrical hill
        elif ((slope > 0.45) and (x < 0) and (x > -h / 4) and
              (abs(escarp_factor - 1) < 0.2)):
            m[k] = 1 + 0.71 * (1 - abs(x) / (escarp_factor * l2_capital))

        # within the region from the ridge2 up to the back l2_capital
        elif x < 0 and x > -escarp_factor * l2_capital:
            m[k] = 1 + (h / (3.5 * (z + l1_capital))) * (1 - abs(x) /
                                                 (escarp_factor * l2_capital))
            if m[k] > 1.71:
                m[k] = 1.71

    return m
