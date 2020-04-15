# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# This file is part of Polyfemos.
#
# Polyfemos is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or any later version.
#
# Polyfemos is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License and
# GNU General Public License along with Polyfemos. If not, see
# <https://www.gnu.org/licenses/>.'
#
# Author: Henrik Jänkävaara
# -----------------------------------------------------------------------------
"""
A function collection to remove outliers from the data

With default values using (242820 x 2) data set
function execution (1 call) times were

+------------+--------+------+
| STALTA     | 1.43 s | 100% |
+------------+--------+------+
| DTR        | 1.19 s |  84% |
+------------+--------+------+
| Lipschitz  | 0.58 s |  41% |
+------------+--------+------+

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
# This module should be as generic as possible.
# Do not import anything polyfemos related.
import math

import numpy as np

from sklearn.tree import DecisionTreeRegressor
from obspy.signal.trigger import classic_sta_lta, trigger_onset


def _get_mask(b, N, indices, nanindices=[]):
    """
    Helper function to form masks

    :type b: bool
    :param b: selects either :func:`~numpy.ones` or
        :func:`~numpy.zeros`.
    :type N: int
    :param N: the length of the mask
    :type indices: :class:`~numpy.ndarray`
    :param indices:
    :type nanindices: :class:`~numpy.ndarray`
    :param nanindices:
    :rtype: :class:`~numpy.ndarray`
    :return: mask array containing bool values
    """
    b = bool(b)
    mask = [np.ones, np.zeros][b](N, dtype=np.float)
    mask[nanindices] = float('nan')
    mask[indices] = b
    return mask


def dtr(data, maxdepth=0, scale=24000, medlim=10, **kwargs):
    """
    A function to remove outliers using
    `Decision Tree <https://en.wikipedia.org/wiki/Decision_tree_learning>`_.

    The given ``data`` is approximated using
    :class:`~sklearn.tree.DecisionTreeRegressor` decision tree.
    The median of the error between the data and the approximation
    is calculated. If the error between a datapoint and an approximated value
    is greater than ``medlim`` times the median, the datapoint is excluded.

    ``scale`` is used to select ``maxdepth`` according to the datalen N.
    If N > ``scale``, ``maxdepth`` = 2.
    If N > 10 * ``scale``, ``maxdepth`` = 4, and so forth.
    If ``maxdepth`` is given, ``scale`` is ignored.

    :type data: :class:`~numpy.ndarray`
    :param data: x-y data in Nx2 array, shape (N, 2)
    :type maxdepth: int
    :param maxdepth: The maximum depth of the tree.
    :type scale: float
    :param scale:
    :type medlim: float
    :param medlim:
    :rtype: :class:`~numpy.ndarray`
    :return: mask array containing bool values
    """
    orig_N = data.shape[0]

    if maxdepth <= 0:
        func_ = \
            lambda x: int(max([1., np.floor(2 * np.log10(10 * x / scale))]))
        maxdepth = func_(orig_N)

    nanbools = np.isnan(data[:, 1])
    nanindices = np.where(nanbools)[0]
    data = data[nanbools == False]

    x = data[:, 0]
    y = data[:, 1].ravel()

    X = x.reshape(data.shape[0], 1)

    regr = DecisionTreeRegressor(max_depth=maxdepth)
    regr.fit(X, y)
    y_pred = regr.predict(X)

    temp = np.abs(np.subtract(y, y_pred))
    median = np.median(temp)

    filter_ = np.vectorize(
        lambda a0, a1: np.abs(a0 - a1) < np.abs(medlim * median))
    xi = np.where(filter_(y, y_pred))[0]

    for i in nanindices:
        xi[i <= xi] += 1

    return _get_mask(True, orig_N, xi, nanindices=nanindices)


def lipschitz(data, itern=1, klim=7e-6, **kwargs):
    """
    A function to remove outliers based on
    `Lipschitz continuity
    <https://en.wikipedia.org/wiki/Lipschitz_continuity>`_.
    Calculates the change (slope, K) in y=f(x) function between two datapoints.

    .. code-block:: text

        K = |f(x1) - f(x0)| / |x1 - x0|

    Datapoints which cause a slope too steep, are removed.

    :type data: :class:`~numpy.ndarray`
    :param data: x-y data in Nx2 array, shape (N, 2)
    :type itern: int
    :param itern: The maximum interval between the datapoints x0 and x1
        Complexity = N * ``itern``
    :type klim: float
    :param klim: the maximum slope allowed
    :rtype: :class:`~numpy.ndarray`
    :return: mask array containing bool values
    """

    itern = max([itern, 1]) + 1

    N = data.shape[0]
    i = -1
    remindices = set({})
    nanindices = set({})

    while True:

        i += 1
        if i >= N:
            break
        if i in remindices:
            continue
        if i in nanindices:
            continue

        x0 = data[i, 0]
        y0 = data[i, 1]

        remc = 0
        invalid_value = False
        j = i + 1
        while True:

            if j >= min([i + itern + remc, N]):
                break

            x1 = data[j, 0]
            y1 = data[j, 1]

            if math.isnan(y1):
                nanindices.add(j)
                invalid_value = True

            else:
                dx = abs(x1 - x0)
                if dx < 99e-99:
                    K = 0
                else:
                    K = abs(y1 - y0) / dx

                if K > klim:
                    remindices.add(j)
                    invalid_value = True
                else:
                    invalid_value = False

            if invalid_value:
                remc += 1
            else:
                remc = 0

            j += 1

    remindices = list(remindices)
    nanindices = list(nanindices)

    return _get_mask(False, N, remindices, nanindices=nanindices)


def stalta(data, nsta=3, nlta=10, threson=1.08, thresoff=1.05, offset=40,
           **kwargs):
    """
    Utilises :func:`~obspy.signal.trigger.classic_sta_lta` to remove outliers

    :type data: :class:`~numpy.ndarray`
    :param data: x-y data in Nx2 array, shape (N, 2)
    :type nsta: int
    :param nsta: Length of short time average window in samples
    :type nlta: int
    :param nlta: Length of long time average window in samples
    :type threson: float
    :param threson: Value above which trigger (of characteristic function)
                    is activated (higher threshold)
    :type thresoff: float
    :param thresoff: Value below which trigger (of characteristic function)
                     is deactivated (lower threshold)
    :type offset: int
    :param offset: in samples, how many additional samples are removed before
                   on trigger and after off trigger
    :rtype: :class:`~numpy.ndarray`
    :return: mask array containing bool values
    """
    orig_N = data.shape[0]

    nanbools = np.isnan(data[:, 1])
    nanindices = np.where(nanbools)[0]
    data = data[nanbools == False]

    cft = classic_sta_lta(data[:, 1], nsta, nlta)
    trigger_onoff = trigger_onset(cft, threson, thresoff)

    def inside_to(x_):
        for to in trigger_onoff:
            if to[0] - offset <= x_ <= to[1] + offset:
                return False
        return True

    filter_ = np.vectorize(inside_to)

    xi = np.where(filter_(np.arange(data.shape[0])))[0]

    for i in nanindices:
        xi[i <= xi] += 1

    return _get_mask(True, orig_N, xi, nanindices=nanindices)
