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
Functions to parse filepaths from strings

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import os
import functools

from polyfemos.parser import typeoperator as to
from polyfemos.parser import resources


# Functions applied to the filepaths
# Selected by the first character of the path
_parents = {
    ".": lambda x: x,
    "/": os.path.abspath,
    "~": os.path.expanduser,
}
# Reversed variables and the system's path separator
_replacers = [
    [resources.VARS["YEAR"], "{year}"],
    [resources.VARS["JULDAY_ZP"], "{julday:0>3}"],
    [resources.VARS["JULDAY"], "{julday}"],
    [resources.VARS["NETWORK"], "{network_code}"],
    [resources.VARS["STATION"], "{station_code}"],
    [resources.VARS["LOCATION"], "{location_code}"],
    [resources.VARS["CHANNEL"], "{channel_code}"],
    [resources.VARS["PARNAME"], "{parname}"],
    ["/", os.path.sep],
]


def _pathfunc(path, year="", julday="", network_code="", station_code="",
              location_code="", channel_code="", parname="", **kwargs):
    """
    :type path: str
    :param path: A filepath body to be filled with reserved variable values
    :type year: str, optional
    :param year: defaults to empty string
    :type julday: str, optional
    :param julday: defaults to empty string
    :type network_code: str, optional
    :param network_code: defaults to empty string
    :type station_code: str, optional
    :param station_code: defaults to empty string
    :type location_code: str, optional
    :param location_code: defaults to empty string
    :type channel_code: str, optional
    :param channel_code: defaults to empty string
    :type parname: str, optional
    :param parname: defaults to empty string
    :rtype: str
    :return: A filepath with every reserved variable replaced with their
        respectable values
    """
    return path.format(year=year, julday=julday, network_code=network_code,
                       station_code=station_code, location_code=location_code,
                       channel_code=channel_code, parname=parname)


def path_from_str(inputstr):
    """
    :type inputstr: str
    :param inputstr: A string representing the filepath, reserved variables
        included
    :rtype: func
    :return: A filepath function
    """
    if len(inputstr) > 0:
        parent = inputstr[0]
        if parent in _parents:
            inputstr = _parents[parent](inputstr)
    # Reserved variables and the path separator are replaced
    # with their approbriate replacers
    for repls in _replacers:
        inputstr = inputstr.replace(*repls)
    return to.replaceNaN(functools.partial(_pathfunc, path=inputstr))


if __name__ == "__main__":

    path = "~/archive/&YEAR/&NETWORK/&STATION/&CHANNEL.D/&YEAR"
    kwargs = {
        "year": 1980,
        "network_code": "FN",
        "station_code": "MSF",
        # "channel_code": "HHZ",
        "asd": "ASD",
    }
    print(path_from_str(path)(**kwargs))
