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
Contains classes for handling station information

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import itertools
import operator

from polyfemos.parser import typeoperator as to
from polyfemos.almanac.ordinal import Ordinal


def get_id(network_code, station_code):
    """
    :type network_code: str
    :param network_code:
    :type station_code: str
    :param station_code:
    :rtype: str
    :return: ``network_code + "." + station_code``, e.g. "FN.MSF"
    """
    return "{}.{}".format(network_code, station_code)


class Station(object):
    """
    Class for handling information of one station
    """
    def __init__(self, network_code="", station_code="", location_code="",
                 locy=0., locx=0., epsg="", digitizer="", sensor="",
                 starttime="", endtime=""):
        """
        :type network_code: str
        :param network_code: Network code, e.g. "FN"
        :type station_code: str
        :param station_code: Code of the station, e.g. "MSF"
        :type location_code: str
        :param location_code: Location of the station, e.g. "00" or empty
        :type locy: float
        :param locy: Y coordinate
        :type locx: float
        :param locx: X coordinate
        :type epsg: str
        :param epsg: EPSG number for ``locx`` and ``locy`` coordinates
        :type digitizer: str
        :param digitizer: Model/name of the station's digitizer
        :type sensor: str
        :param sensor: Model/name of the station's sensor
        :type starttime: :class:`~polyfemos.almanac.ordinal.Ordinal`
        :param starttime:
        :type endtime: :class:`~polyfemos.almanac.ordinal.Ordinal`
        :param endtime:
        """
        self.network_code = network_code
        self.station_code = station_code
        self.code = station_code
        self.location_code = \
            "" if to.isStrNaN(location_code) else location_code

        self.locy = locy
        self.locx = locx
        self.epsg = epsg
        self.digitizer = digitizer
        self.sensor = sensor

        if endtime.timestamp < starttime.timestamp:
            starttime, endtime = endtime, starttime
        self.starttime = starttime
        self.endtime = endtime

        self.parameters = []
        self.id = self.get_id()
        self.header = None

    def get_id(self):
        """
        :rtype: str
        :return: e.g. "FN.MSF"
        """
        return get_id(self.network_code, self.station_code)

    def covers_time(self, t0):
        """
        :type t0: :class:`~polyfemos.almanac.ordinal.Ordinal`
        :param t0:
        :rtype: bool
        :return: ``True`` if ``t0`` is between ``self.starttime`` and
            ``self.endtime``
        """
        return self.starttime.timestamp <= t0 <= self.endtime.timestamp

    def add_parameter(self, parameter):
        """
        :type parameter: :class:`~polyfemos.back.parameter.Parameter`
        :param parameter:
        """
        self.parameters.append(parameter)

    def filter_parameters(self, **kwargs):
        """
        Filters ``self.parameters`` according to given ``kwargs``.
        The values of the kwargs should be list of values, or one value.
        If given keyword argument is attribute of the
        :class:`~polyfemos.back.parameter.Parameter` class,
        and the given value(s)
        are not equal to the the parameter, the parameter is excluded.
        """
        for key, value in kwargs.items():
            if not isinstance(value, list):
                value = [value]
            if len(value) <= 0 \
                    or all(map(to.isStrNaN, value)) \
                    or not any(value):
                continue
            self.parameters = \
                [par for par in self.parameters if par[key] in value]

    def _add_to_header(self, field, *args):
        """
        Any number of ``args`` can be provided, and are processed into a
        string repsentation of a list. Each arg is converted into a string as
        follows:
        ``None`` -> ``""``, empty string
        ``float('nan')`` -> ``"NaN"``
        ``""`` -> ``"NaN"``
        ``stringvalue -> "stringvalue"``
        ``123 -> "123"``

        :type field: str
        :param field:
        """
        def check_arg(arg):
            if arg is None:
                return ""
            if isinstance(arg, (int, float)) and to.isNaN(arg):
                return to.strNaN()
            arg = str(arg)
            return arg if arg else to.strNaN()

        if len(args) <= 0:
            return
        args = map(check_arg, args)
        if self.header is None:
            self.header = ""
        self.header += "{} {}\n".format(field, ",".join(args))

    def create_header(self):
        """
        Creates the soh text file header
        """
        self.header = ""
        self._add_to_header("HEADER", None)
        self._add_to_header("ID", self.id)
        self._add_to_header("NETWORK", self.network_code)
        self._add_to_header("STATION", self.station_code)
        self._add_to_header("LOCATION", self.location_code)
        self._add_to_header("SENSOR", self.sensor)
        self._add_to_header("DIGITIZER", self.digitizer)
        self._add_to_header("STARTTIME", self.starttime)
        self._add_to_header("ENDTIME", self.endtime)
        self._add_to_header("LOCY", self.locy)
        self._add_to_header("LOCX", self.locx)
        self._add_to_header("EPSG", self.epsg)
        for par in self.parameters:
            for field, args in par.generate_header():
                self._add_to_header(field, *args)
        self._add_to_header("DATA", None)

    def get_header(self, force=False):
        """
        :type force: bool, optional
        :param force: defaults to ``False``, if ``True`` the header is
            recreated even if it already exists
        :rtype: str
        :return: the header of the 'stf' file
        """
        if self.header is None or force:
            self.create_header()
        return self.header

    def _compare(self, op, other):
        """
        Compares starttimes of the stations ``self`` and ``other``.
        If station ids do not match, always returns ``False``.

        :type op: func
        :param op: comparison operation, e.g. :func:`~operator.lt`
        :type other: :class:`~polyfemos.back.station.Station`
        :param other:
        :rtype: bool
        :return:
        """
        if self != other:
            return False
        return op(self.starttime.timestamp, other.starttime.timestamp)

    def __lt__(self, other):
        """
        see :meth:`~polyfemos.back.station.Station._compare` for more info

        :type other: :class:`~polyfemos.back.station.Station`
        :param other:
        :rtype: bool
        :return:
        """
        return self._compare(operator.lt, other)

    def __gt__(self, other):
        """
        see :meth:`~polyfemos.back.station.Station._compare` for more info

        :type other: :class:`~polyfemos.back.station.Station`
        :param other:
        :rtype: bool
        :return:
        """
        return self._compare(operator.gt, other)

    def __le__(self, other):
        """
        see :meth:`~polyfemos.back.station.Station._compare` for more info

        :type other: :class:`~polyfemos.back.station.Station`
        :param other:
        :rtype: bool
        :return:
        """
        return self._compare(operator.le, other)

    def __ge__(self, other):
        """
        see :meth:`~polyfemos.back.station.Station._compare` for more info

        :type other: :class:`~polyfemos.back.station.Station`
        :param other:
        :rtype: bool
        :return:
        """
        return self._compare(operator.ge, other)

    def __eq__(self, other):
        """
        :type other: :class:`~polyfemos.back.station.Station`
        :param other:
        :rtype: bool
        :return: returns ``True`` if ids of ``self`` and ``other``
            are identical
        """
        return self.id == other.id

    def __ne__(self, other):
        """
        :type other: :class:`~polyfemos.back.station.Station`
        :param other:
        :rtype: bool
        :return: opposite of :meth:`~polyfemos.back.station.Station.__eq__`
        """
        return not self == other

    def __str__(self):
        """
        :rtype: str
        :return: somekind of string to represent the station
        """
        return "{:8}{:28}{:28}".format(self.id, self.starttime, self.endtime)

    def __len__(self):
        """
        :rtype: int
        :return: How many parameters the station has
        """
        return len(self.parameters)


class Stations(object):
    """
    Class for containing and handling multiple
    :class:`~polyfemos.back.station.Station`
    instances
    """
    def __init__(self):
        """
        """
        self.__stations = {}
        self.__last_id = ""

    def add_station(self, station):
        """
        Adds ``station`` to ``self.__stations``.
        If successsfully added, the id of the ``station`` is saved as
        ``self.__last_id``. ``self.__last_id`` will always contain the is of
        the last successfully added station.

        :type station: :class:`~polyfemos.back.station.Station`
        :param station:
        :rtype: bool
        :return: ``True`` if ``station`` was successfully added to the
            ``self.__stations``
        """
        id_ = station.id
        if id_ not in self.__stations:
            self.__stations[id_] = []
        else:
            # Check if the given start or endtime are already present
            # with the given id
            prod = itertools.product(
                self.__stations[id_],
                [station.starttime, station.endtime]
            )
            if any(x[0].covers_time(x[1]) for x in prod):
                return False
        self.__stations[id_].append(station)
        self.__last_id = id_
        return True

    def get_station(self, network_code, station_code, t0):
        """
        :type network_code: str
        :param network_code:
        :type station_code: str
        :param station_code:
        :type t0: :class:`~polyfemos.almanac.ordinal.Ordinal`
        :param t0:
        :rtype: :class:`~polyfemos.back.station.Station`
        :return: returns station instances matching the given ``network_code``
            and ``station_code``, and including ``t0`` within it's time
            interval
        """
        id_ = get_id(network_code, station_code)
        if id_ not in self.__stations:
            return None
        for station in self.__stations[id_]:
            if station.covers_time(t0):
                return station
        return None

    def add_parameter(self, parameter):
        """
        Adds ``parameter`` to the last station with id ``self.__last_id``

        :type parameter: :class:`~polyfemos.back.parameter.Parameter`
        :param parameter:
        """
        self.__stations[self.__last_id][-1].add_parameter(parameter)


if __name__ == "__main__":

    station1 = Station(
        station_code="D",
        starttime=Ordinal(1970, 1, 1), endtime=Ordinal(1975, 1, 1))
    station2 = Station(
        station_code="D",
        starttime=Ordinal(1975, 1, 1), endtime=Ordinal(2001, 1, 1))
    station3 = Station(
        station_code="D",
        starttime=Ordinal(1970, 1, 1), endtime=Ordinal(2001, 1, 1))

    stations = Stations()
    print(stations.add_station(station1))
    print(stations.add_station(station2))
    print(stations.add_station(station3))

    print(station1 < station2)
    print(station1 <= station2)
    print(station1 > station2)
    print(station1 >= station2)
    print(station1 < station3)
    print(station1 <= station3)
    print(station1 > station3)
    print(station1 >= station3)

    print(station1 == station2)
    print(station1 == station3)
    print(station1 != station2)
    print(station1 != station3)
