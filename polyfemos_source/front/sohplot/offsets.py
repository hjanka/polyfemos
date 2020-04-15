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
Contains class :class:`~polyfemos.front.sohplot.offsets.UWVOffsets`.

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
from polyfemos.parser import typeoperator as to
from polyfemos.front import userdef


OFFSET_U = ""
OFFSET_W = ""
OFFSET_V = ""
OFFSET_N = ""
OFFSET_E = ""
OFFSET_Z = ""
NEZ_OFFSETS = {}


def init_definitions():
    """
    Updates the definition values with userdefined values
    from YAML files.
    """
    global OFFSET_U
    OFFSET_U = userdef.definitions("offset_u")
    global OFFSET_W
    OFFSET_W = userdef.definitions("offset_w")
    global OFFSET_V
    OFFSET_V = userdef.definitions("offset_v")
    global OFFSET_N
    OFFSET_N = userdef.definitions("offset_n")
    global OFFSET_E
    OFFSET_E = userdef.definitions("offset_e")
    global OFFSET_Z
    OFFSET_Z = userdef.definitions("offset_z")
    global NEZ_OFFSETS
    NEZ_OFFSETS = {OFFSET_N, OFFSET_E, OFFSET_Z}


class UWVOffsets(object):
    """
    A class for UWV to NEZ conversion

    The transforming function for each sensor is defined in
    :func:`~polyfemos.front.userdef.transform_func`
    """
    def __init__(self):
        """
        """
        init_definitions()
        self.clear()

    def clear(self):
        """
        Initializes ``self.offsets`` attribute into it's default value.
        """
        self.offsets = {
            OFFSET_U: {"value": "NaN", "dt": ""},
            OFFSET_W: {"value": "NaN", "dt": ""},
            OFFSET_V: {"value": "NaN", "dt": ""},
        }

    def update(self, dtstr, key, value):
        """
        Stores given ``value`` to offset U, W or V.

        :type dtstr: str
        :param dtstr: datetime compatible string or other value compatible
            with :class:`~obspy.core.utcdatetime.UTCDateTime`
        :type key: str
        :param key: Which offset is updated, U, W or V
        :type value: str
        :param value: string representing float value of the offset,
        """
        if key not in self.offsets:
            return
        self.offsets[key]["value"] = to.float_(value)
        self.offsets[key]["dt"] = to.utcdatetime(dtstr)

    def transform(self, sensor, component):
        """
        Transform offsets, UWV to NEZ

        :type sensor: str
        :param sensor: Which transformation function is used,
            defined in :func:`~polyfemos.front.userdef.transform_func`
        :type conponent: str
        :param conponent: Which component after transformation is returned,
            N, E or Z.
        :rtype: :class:`~obspy.core.utcdatetime.UTCDateTime`, float
        :return: timevalue and value of N, E or Z offset
        """
        u = self.offsets[OFFSET_U]["value"]
        w = self.offsets[OFFSET_W]["value"]
        v = self.offsets[OFFSET_V]["value"]
        # Transform UWV to NEZ
        x, y, z = userdef.transform_func(sensor)(u, v, w)
        # make list of time values
        list_ = [
            self.offsets[OFFSET_U]["dt"],
            self.offsets[OFFSET_W]["dt"],
            self.offsets[OFFSET_V]["dt"],
        ]
        # Takes the middle timestamp as the offset time value
        dt = sorted(list_, key=lambda dt: dt.timestamp)[1]
        return dt, {"N": y, "E": x, "Z": z}[component]

    def isnan(self):
        """
        Checks if every value (U, W and V) is defined. If every one is defined,
        the coordinate transformation can be done.

        :rtype: bool
        :return: returns ``False`` if the coordinate trasformation is possible.
        """
        for v in self.offsets.values():
            if v["value"] == "NaN":
                return True
        return False

    def __bool__(self):
        """
        :rtype: bool
        :return: returns ``True`` if the coordinate trasformation is possible.
        """
        return not self.isnan()
