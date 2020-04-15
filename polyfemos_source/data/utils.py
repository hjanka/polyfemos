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
Miscellanous data manipulation functions

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import numpy as np


def log10_decimation(data, maxn=100):
    """
    Remove datapoints logarithmicly
    remove every n datapoints starting from 0, ending maxn-1
    n increases exponentially
    Mainly used for logarithmic plotting where there are
    too many datapoints to be properly plot

    Returns decimated data as list

    :type data: list or array-like
    :param data: data array to be decimated
    :type maxn: int
    :param maxn: defines the amount of decimation made
    :rtype: list
    :return: Logarithmically decimated list
    """
    len_ = len(data)
    maxexp = np.log10(maxn)
    exps = np.arange(0, maxexp, maxexp / len_)

    indices = []
    i = 0
    while i < len_:
        indices.append(i)
        i += int(10 ** exps[i])

    return [data[i] for i in indices]
