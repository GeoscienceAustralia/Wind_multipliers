"""
:mod:`blrb` -- Functions for BiLinear Recursive Bisection (BLRB).

All shape references here follow the numpy convention (nrows, ncols), which
makes some of the code harder to follow.
===============================================================================

:moduleauthor: Roger Edberg (roger.edberg@ga.gov.au)
"""

import numpy
import logging
from utilities.meta import print_call
from meta import print_call
import math

LOGGER = logging.getLogger('root.' + __name__)

DEFAULT_ORIGIN = (0, 0)
DEFAULT_SHAPE = (8, 8)


@print_call(LOGGER.debug)
def bilinear(shape, f_ul, f_ur, f_lr, f_ll, dtype=numpy.float64):
    """
    Bilinear interpolation of four scalar values.

    :param shape:
        Shape of interpolated grid (nrows, ncols).

    :param f_ul:
        Data value at upper-left (NW) corner.

    :param f_ur:
        Data value at upper-right (NE) corner.

    :param f_lr:
        Data value at lower-right (SE) corner.

    :param f_ll:
        Data value at lower-left (SW) corner.

    :param dtype:
        Data type (numpy I presume?).

    :return:
        Array of data values interpolated between corners.
    """

    s, t = [a.astype(dtype) for a in numpy.ogrid[0:shape[0], 0:shape[1]]]

    s /= (shape[0] - 1.0)
    t /= (shape[1] - 1.0)

    return s * (t * f_lr + (1.0 - t) * f_ll) + \
        (1.0 - s) * (t * f_ur + (1.0 - t) * f_ul)


@print_call(LOGGER.debug)
def indices(origin=DEFAULT_ORIGIN, shape=DEFAULT_SHAPE):
    """
    Generate corner indices for a grid block.

    :param origin:
        Block origin (2-tuple).

    :param shape:
        Block shape (2-tuple: nrows, ncols).

    :return:
        Corner indices: (xmin, xmax, ymin, ymax).
    """
    return (origin[0], origin[0] + shape[0] - 1,
            origin[1], origin[1] + shape[1] - 1)


@print_call(LOGGER.debug)
def subdivide(origin=DEFAULT_ORIGIN, shape=DEFAULT_SHAPE):
    """
    Generate indices for grid sub-blocks.

    :param origin:
        Block origin (2-tuple).

    :param shape:
        Block shape (nrows, ncols).

    :return:
        Dictionary containing sub-block corner indices:
            { 'UL': <list of 2-tuples>,
              'UR': <list of 2-tuples>,
              'LL': <list of 2-tuples>,
              'LR': <list of 2-tuples> }
    """
    i0, ie, j0, je = indices(origin, shape)
    ic = origin[0] + shape[0] / 2
    jc = origin[1] + shape[1] / 2

    return {
        'UL': [(i0, j0), (i0, jc), (ic, j0), (ic, jc)],
        'LL': [(ic, j0), (ic, jc), (ie, j0), (ie, jc)],
        'UR': [(i0, jc), (i0, je), (ic, jc), (ic, je)],
        'LR': [(ic, jc), (ic, je), (ie, jc), (ie, je)],
    }


@print_call(LOGGER.debug)
def interpolate_block(origin=DEFAULT_ORIGIN, shape=DEFAULT_SHAPE,
                      eval_func=None, grid=None):
    """
    Interpolate a grid block.

    :param origin:
        Block origin (2-tuple).

    :param shape:
        Block shape (nrows, ncols).

    :param eval_func:
        Evaluator function.
    :type eval_func:
        callable; accepts grid indices i, j and returns a scalar value.

    :param grid:
        Grid array.
    :type grid:
        :py:class:`numpy.array`.

    :return:
        Interpolated block array if grid argument is None. If grid argument
        is supplied its elements are modified in place and this function
        does not return a value.
    """
    i0, i1, j0, j1 = indices(origin, shape)

    # Indices need to be integers - no fraction allowed
    i0 = math.floor(i0)
    j0 = math.floor(j0)
    i1 = math.ceil(i1)
    j1 = math.ceil(j1)

    f_ul = eval_func(i0, j0)
    f_ll = eval_func(i1, j0)
    f_ur = eval_func(i0, j1)
    f_lr = eval_func(i1, j1)

    if grid is None:
        return bilinear(shape, f_ul, f_ur, f_lr, f_ll)

    grid[i0:i1 + 1, j0:j1 + 1] = bilinear(shape, f_ul, f_ur, f_lr, f_ll)


@print_call(LOGGER.debug)
def interpolate_grid(depth=0, origin=DEFAULT_ORIGIN, shape=DEFAULT_SHAPE,
                     eval_func=None, grid=None):
    """
    Interpolate a data grid.

    :param depth:
        Recursive bisection depth.
    :type depth:
        :py:class:`int`

    :param origin:
        Block origin,
    :type origin:
        :py:class:`tuple` of length 2.

    :param shape:
        Block shape.
    :type shape:
        :py:class:`tuple` of length 2 ``(nrows, ncols)``.

    :param eval_func:
        Evaluator function.
    :type eval_func:
        callable; accepts grid indices i, j and returns a scalar value.

    :param grid:
        Grid array.
    :type grid:
        :py:class:`numpy.array`.

    :todo:
        Move arguments ``eval_func`` and ``grid`` to positions 1 and 2, and
        remove defaults (and the check that they are not ``None`` at the top
        of the function body).
    """
    assert eval_func is not None
    assert grid is not None

    if depth == 0:
        interpolate_block(origin, shape, eval_func, grid)
    else:
        blocks = subdivide(origin, shape)
        for (k_ul, k_ur, k_ll, k_lr) in blocks.values():
            block_shape = (k_lr[0] - k_ul[0] + 1, k_lr[1] - k_ul[1] + 1)
            interpolate_grid(depth - 1, k_ul, block_shape, eval_func, grid)
