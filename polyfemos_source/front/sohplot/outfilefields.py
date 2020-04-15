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
Type structure for '\*.stf' file header fields and data rows, and for
'\*.alert' and '\*.csv' file data rows.

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
from polyfemos.parser import typeoperator as to


def floatlist(inputstr, length=2):
    """
    :type inputstr: str
    :param inputstr: a string passed to
        :func:`~polyfemos.parser.typeoperator.floatlist`
    :type length: int, optional
    :param length: if the formed list does not match the given ``length``,
        ``None`` is returned.
    :rtype: list
    :return: list of floats or ``None``, if formation of list was not possible
         with given ``inputstr``
    """
    list_ = to.floatlist(inputstr)
    if list_ is None or len(list_) != length:
        return None
    return list_


def alert(inputstr):
    """
    :type inputstr: str
    :param inputstr:
    :rtype: str
    :return: Returns ``None`` if given ``inputstr`` didn't contain valid
        alert information.
    """
    if inputstr not in {"0", "1", "2", "nan"}:
        return None
    return inputstr


def string(inputstr):
    """
    :type inputstr: str
    :param inputstr: string passed to
        :func:`~polyfemos.parser.typeoperator.str_`
    :rtype: str
    :return: If ``inputstr`` is empty, ``None`` is returned.
    """
    return to.str_(inputstr, check_empty=True)


_error_msg = {
    "utcdatetime": "No UTC datetime compatible string. ",
    "str": "Empty string found. ",
    "float": "Invalid type, should be float. ",
    "int": "Invalid type, should be int. ",
    "dict": "Malformed dictionary. ",
    "floatlist": "The value should be a list of two floats. "
                 "The list may contain 'NaN' string values. ",
    "alert": "The value should be '0', '1', '2', or 'nan'. ",
}


# State of health text file's available header fields.
# The first column in the list is the type of the actual value as a function.
# The second column in the list is a message in case of erroneous type
# conversion.
# The third column is the default value
STF_HEADER = {
    "ID": [string, _error_msg["str"], ""],
    "NETWORK": [string, _error_msg["str"], ""],
    "STATION": [string, _error_msg["str"], ""],
    "LOCATION": [string, _error_msg["str"], ""],
    "SENSOR": [string, _error_msg["str"], ""],
    "DIGITIZER": [string, _error_msg["str"], ""],
    "STARTTIME": [to.utcdatetime, _error_msg["utcdatetime"], 0],
    "ENDTIME": [to.utcdatetime, _error_msg["utcdatetime"], 0],
    "LOCY": [to.float_, _error_msg["float"], 0],
    "LOCX": [to.float_, _error_msg["float"], 0],
    "EPSG": [string, _error_msg["str"], ""],
    "UNIT": [string, _error_msg["str"], ""],
    "PRIORITY": [to.int_, _error_msg["int"], 0],
    "PLOTLIMS": [floatlist, _error_msg["floatlist"], []],
    "IRLIMS": [floatlist, _error_msg["floatlist"], []],
    "YELLOW": [floatlist, _error_msg["floatlist"], []],
    "ORANGE": [floatlist, _error_msg["floatlist"], []],
    "RED": [floatlist, _error_msg["floatlist"], []],
}

# The first column is either 1 or 0, for mandatory (1) or optional (0) value.
# The second column is the type of the actual value as a function.
# The third row is a message in case of erroneous type conversion.
STF_DATA = [
    [1, to.utcdatetime, _error_msg["utcdatetime"]],
    [1, string, _error_msg["str"]],
    [1, to.float_, _error_msg["float"]],
    [0, to.dict_, _error_msg["dict"]],
]
CSV_DATA = [
    [1, to.float_, _error_msg["float"]],
    [1, to.float_, _error_msg["float"]],
    [0, to.dict_, _error_msg["dict"]],
]
ALERT_DATA = [
    [1, string, _error_msg["str"]],
    [1, string, _error_msg["str"]],
    [1, alert, _error_msg["alert"]],
    [0, to.int_, _error_msg["int"]],
    [0, to.float_, _error_msg["float"]],
]
