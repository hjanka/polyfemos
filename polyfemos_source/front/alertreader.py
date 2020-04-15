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
Functions for reading state of health alert files ('\*.alert')

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
from obspy import UTCDateTime

from polyfemos.front import request
from polyfemos.util import fileutils


def get_sohdict(station_ids, year, julday, fpf, realtimeness=None):
    r"""
    Reads state of health alert ('\*.alert') files. Extracts the data
    for all ``station_ids``, if available. The date of the alert file is
    defined by ``year`` and ``julday`` (day of the year).

    :type station_ids: list
    :param station_ids: A list of string consisting of station codes together
        with network code, for example "FN.MSF"
    :type year: numlike
    :param year:
    :type julday: numlike
    :param julday:
    :type fpf: func
    :param fpf: filepath format leading to an alert file
    :type realtimeness: :class:`~obspy.core.utcdatetime.UTCDateTime` or
        int or float or None
    :param realtimeness: Defaults to ``None``. If proper ``realtimeness`` is
        given, alerts with the last datapoint timevalue lesser than
        ``realtimeness``, are changed to ``"nan"``
    :rtype: dict
    :return: A dictionary consisting of 'alerts' and 'priorities' dictionaries
        with each station and sohpar combination
    """
    if realtimeness is not None:
        if isinstance(realtimeness, UTCDateTime):
            realtimeness = realtimeness.timestamp
        if not isinstance(realtimeness, (float, int)):
            realtimeness = None

    sohdict = {}
    sohdict['alerts'] = {}
    sohdict['priorities'] = {}
    sohdict['ldts'] = {}
    pathkwargs = {}
    pathkwargs['year'] = year
    pathkwargs['julday'] = julday

    for station_id in station_ids:
        network_code, station_code = station_id.split(".")
        pathkwargs['network_code'] = network_code
        pathkwargs['station_code'] = station_code
        filepath = request.filepath(fpf(**pathkwargs), ".alert")
        rows = fileutils.read_csv(filepath)
        if rows is None:
            continue
        for row in rows[1:]:
            # Fill the rows with inadequate length with empty strings
            station_id_temp, parameter, alert, priority, ldt = \
                row + [""] * max([5 - len(row), 0])
            key = station_id_temp + parameter

            if realtimeness is not None:
                if not ldt or float(ldt) < realtimeness:
                    alert = "nan"

            sohdict['alerts'][key] = alert
            sohdict['priorities'][key] = priority

    return sohdict
