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
Contains :class:`~polyfemos.almanac.ordinal.Ordinal` class

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
from obspy import UTCDateTime


class Ordinal(UTCDateTime):
    """
    A class for treating dates as years and days of the year, with a
    precicion of 1 day.
    """
    def __init__(self, *args, **kwargs):
        """
        If no arguments are given, returns the current date, at 12am UTC

        see :class:`~obspy.core.utcdatetime.UTCDateTime` for more information
        about the ``args`` and ``kwargs``
        """
        utcdt = None
        for arg in args:
            if isinstance(arg, UTCDateTime):
                utcdt = arg
        if len(args) == 0 and len(kwargs) == 0:
            utcdt = UTCDateTime()
        if utcdt is None:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(year=utcdt.year, julday=utcdt.julday)

    def shiftdays(self, a):
        """
        see :meth:`~polyfemos.almanac.ordinal.Ordinal.__iadd__`

        :type a: int
        :param a:
        :rtype: :class:`~polyfemos.almanac.ordinal.Ordinal`
        :return:
        """
        return self.__iadd__(a)

    def __iadd__(self, a):
        """
        Adds ``a`` days to the current date

        :type a: int
        :param a:
        :rtype: :class:`~polyfemos.almanac.ordinal.Ordinal`
        :return:
        """
        return Ordinal(self + 86400. * a)

    def __isub__(self, a):
        """
        Substracts ``a`` days from the current date

        :type a: int
        :param a:
        :rtype: :class:`~polyfemos.almanac.ordinal.Ordinal`
        :return:
        """
        return self.__iadd__(-1 * a)

    def __format__(self, a):
        """
        Adds a possibility to use python's format function

        >>> "{}".format(Ordinal)

        :type a:
        :param a:
        :rtype: str
        :return:
        """
        return str(self).__format__(a)

    @staticmethod
    def today():
        """
        A static method

        :rtype: :class:`~polyfemos.almanac.ordinal.Ordinal`
        :return: A current date at 12am UTC
        """
        return Ordinal()

    @staticmethod
    def range(starttime, endtime, step=1):
        """
        A static method

        Alternatively, ``starttime`` and ``endtime`` can be given as datatypes
        accepted by :class:`~obspy.core.utcdatetime.UTCDateTime` constructor.

        :type starttime: :class:`~polyfemos.almanac.ordinal.Ordinal`
        :param starttime:
        :type endtime: :class:`~polyfemos.almanac.ordinal.Ordinal`
        :param endtime:
        :type step: int, optional
        :param step: defaults to 1, the step size of the date sequence
            in days.
        :rtype: generator
        :return: A generator yielding
            :class:`~polyfemos.almanac.ordinal.Ordinal`
            dates between ``starttime`` and ``endtime``, including both.
        """
        time_ = Ordinal(starttime, precision=0)
        while time_ <= endtime:
            yield time_
            time_ += step

    def till(self, endtime, step=1):
        """
        See :meth:`~polyfemos.almanac.ordinal.Ordinal.range` for more info.

        :type endtime: :class:`~polyfemos.almanac.ordinal.Ordinal`
        :param endtime:
        :type step: int, optional
        :param step: defaults to 1, the step size of the date sequence
            in days.
        :rtype: generator
        :return: A generator yielding
            :class:`~polyfemos.almanac.ordinal.Ordinal`
            dates between ``self`` and ``endtime``, including both.
        """
        return Ordinal().range(self, endtime, step=step)

    def getstr(self, sep="-"):
        """
        :type sep: str, optional
        :param sep: defaults to hyphen
        :rtype: str
        :return: A string representation of the date, year and the day of the
            year, separated with ``sep``.
        """
        format_ = "%Y{}%j".format(sep)
        return self.strftime(format_)

    def utcdatetime(self):
        """
        :rtype: :class:`~obspy.core.utcdatetime.UTCDateTime`
        :return: returns the current
            :class:`~polyfemos.almanac.ordinal.Ordinal`
            instance as :class:`~obspy.core.utcdatetime.UTCDateTime`
        """
        # Pretty advanced way to turn Ordinal into obspy UTCDateTime
        # Don't you think. This method calls UTCDateTime.__add__ method
        # in order to do the conversion.
        return self + 0


if __name__ == "__main__":
    print([Ordinal()], type([Ordinal()][0]))
    print(Ordinal())
    print(Ordinal().today())
    ordinal = Ordinal("2018-001")
    for i in range(5):
        ordinal += 1
        print(ordinal.getstr(), ordinal.year, ordinal.julday)
    for i in range(10):
        ordinal -= 1
        print(ordinal.getstr(sep="."), str(ordinal))

    today = UTCDateTime()
    print(Ordinal(today))
