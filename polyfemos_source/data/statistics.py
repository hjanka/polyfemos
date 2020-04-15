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
Functions for retrieving statistical info about the data

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import math

import numpy as np


def get_statistics_dict(data, thresholds=[], unit=float('nan')):
    """
    Calculates statistical parameters of the given data

    :type data: list
    :param data: 1-D data, without nans
    :type thresholds: list, optional
    :param thresholds: Upper and lower thresholds as a list of at most
        two entries, used to calculate broken threshold percentage
    :type unit: str, optional
    :param unit: The unit of the data
    :rtype: dict
    :return: dictionary containing statistical information of the given data
    """

    def round_to_n(x_, n):
        return np.round_(x_, decimals=n)

    thresholds = thresholds[:2]

    dict_ = {}
    dict_["Median"] = float('nan')
    dict_["Min"] = float('nan')
    dict_["Max"] = float('nan')
    dict_["Mean"] = float('nan')
    dict_["SD"] = float('nan')
    dict_["CV%"] = float('nan')
    dict_["TIB%"] = float('nan')
    dict_["Lower"] = float('nan')
    dict_["Higher"] = float('nan')
    dict_["UNIT"] = unit

    if len(data) <= 0:
        return dict_

    mean = np.mean(data)
    std = np.std(data)

    # Coefficient of variation
    # Actually not very usefull, because same parameters
    # have negative values
    if not (math.isnan(std) or math.isnan(mean) or mean < 10e-99):
        cv = 100.0 * std / mean
        dict_["CV%"] = round_to_n(cv, 2)

    dict_["Median"] = round_to_n(np.median(data), 2)
    dict_["Min"] = round_to_n(np.min(data), 2)
    dict_["Max"] = round_to_n(np.max(data), 2)
    dict_["Mean"] = round_to_n(mean, 2)
    dict_["SD"] = round_to_n(std, 2)

    percentage = float('nan')
    lower = float('nan')
    higher = float('nan')

    if len(thresholds) > 0:
        lower = min(thresholds)
        higher = max(thresholds)

        def threshold_is_broken(x):
            if lower == higher:
                return x < lower
            else:
                return not (lower <= x <= higher)

        percentage = sum(map(threshold_is_broken, data))
        percentage /= len(data)
        percentage *= 100.0

    dict_["TIB%"] = round_to_n(percentage, 2)
    dict_["Lower"] = lower
    if lower != higher:
        dict_["Higher"] = higher

    return dict_


def get_statistics_table(dict_):
    """
    :type dict\_: dict
    :param dict\_: statistics dictionary
    :rtype: list
    :return: a 2-D list containing statistical information about the
        selected parameter during selected timespan,
        each row in table consists of parameter, value and unit
    """
    if dict_ is None:
        return [[]]
    dict_ = dict_.copy()
    unit0 = dict_.pop("UNIT") if "UNIT" in dict_ else ""
    table = []
    for k, v in dict_.items():
        unit = "%" if k in {"CV%", "TIB%"} else unit0
        table.append([k, v, unit])
    return table
