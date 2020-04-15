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
r"""
Reads Earth Data LOG files

Includes :func:`~polyfemos.back.seismic.edlogreader.get_data` function for
extracting data from Earth Data LOG files

Extracts 1 datapoint per day (this is everthing that is available).
Other state of health parameters are available as MSEED files containing
continuous data.

Parameters available using :func:`~polyfemos.back.seismic.edlogreader.get_data`
``key`` in parentheses

- latitude (lat)
- longitude (long)
- date (date), a string containing year, month and day
- time (time), a string containing hour, minute and second
- heading (hdng) *
- magnetic variation (mva) *
- velocity (vel) *
- 16 bit phase error in 1 second pll (plle) **

| *  Are these important? Do they contain any useful information?
| ** Also available as MSEED so better to use that

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
from polyfemos.parser import typeoperator as to
from polyfemos.util import fileutils


def _ed_log_replacer(str_):
    """
    The function is used to replace some string in the Earth Data LOG file
    to their respective ``key`` names

    :type str\_: str
    :param str\_:
    :rtype: str
    :return: A string with some values replaced
    """
    rlist = [
        [r"\x00", ""],
        [":", ""],
        ["latitude", "lat"],
        ["longitude", "long"],
        ["heading", "hdng"],
        ["velocity", "vel"],
        ["magnetic variation", "mva"],
        ["16 bit phase error in 1 second pll", "plle"],
    ]
    for r in rlist:
        str_ = str_.replace(*r)
    return str_


def _ed_log_get_value_from_rows(rows, key):
    """
    Searches for ``key`` in rows
    If the ``key`` is found, returns the value to the 'right' of the key

    :type rows: list
    :param rows: list of lists of strings
    :type key: str
    :param key:
    :rtype: None, str
    :return: Value corresponding to the key or ``None``
        if the key is not found in ``rows``
    """
    for row in rows:
        if key not in row:
            continue
        # Look for key, index=i
        # then try to return value next to it, (i+1)
        i = row.index(key) + 1
        if i >= len(row):
            continue
        return row[i]
    return None


def _ed_log_valid_row(row):
    """
    Used to filter out rows which does not contain desired information

    :type row: list
    :param row:
    :rtype: bool
    :return:
    """
    if "GPS" in row:
        return True
    if "plle" in row:
        return True
    return False


def _ed_log_parse_row(row):
    """
    Converts a (binary) string ``row`` to list

    :type row: str
    :param row: (binary) string
    :rtype: list
    :return: A modified ``row``
    """
    row = row.strip()
    row = str(row)
    row = row.strip("'")
    row = _ed_log_replacer(row)
    row = [r for r in row.split() if r]
    return row


@fileutils.check_filepath
def get_data(path="", key="", scale=lambda x: x):
    """
    :type path: str
    :param path: filename of the Earth Data LOG file
    :type key: str
    :param key: A value to be extracted
    :rtype: float or None
    :return: A single float value read from ED log file,
        If somenthing went wrong (e.g. the path was invalid), return ``None``.
    """
    rows = fileutils.read_file(path, mode="rb")

    # Convert every row into a list
    rows = (_ed_log_parse_row(row) for row in rows)
    # Filter out unnecessary rows
    rows = [row for row in rows if _ed_log_valid_row(row)]

    value = _ed_log_get_value_from_rows(rows, key)

    value = to.float_(value)
    if value is None:
        return None

    return scale(value)
