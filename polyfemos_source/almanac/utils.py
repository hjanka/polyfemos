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
Collection of miscellanous date functions

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
from datetime import date

from obspy import UTCDateTime

from polyfemos.parser import typeoperator as to


def parse_date(datestr):
    """
    If empty ``datestr`` is give, today is returned

    :type datestr: str or :class:`~datetime.date` or
        :class:`~obspy.core.utcdatetime.UTCDateTime`
    :param datestr: date in format 'YEAR-MONTH-DAY' or 'YEAR-JULDAY'
    :rtype: :class:`~obspy.core.utcdatetime.UTCDateTime`
    :return:
    """
    if not datestr:
        return UTCDateTime.now()
    if isinstance(datestr, UTCDateTime):
        return datestr
    if isinstance(datestr, date):
        return UTCDateTime(str(datestr))
    datetuple = [to.int_(x) for x in datestr.split("-")]
    if any(x is None for x in datetuple):
        return None
    if len(datetuple) == 2:
        return UTCDateTime("{}{:0>3}".format(*datetuple))
    return to.utcdatetime(datestr)


def get_jY(date_):
    r"""
    :type date\_: :class:`~datetime.date` or
        :class:`~obspy.core.utcdatetime.UTCDateTime`.
    :param date\_:
    :rtype: int, int
    :return: the day of the year and the year of given ``date_``
    """
    if isinstance(date_, UTCDateTime):
        return date_.julday, date_.year
    elif isinstance(date_, date):
        return date_.timetuple().tm_yday, date_.year
    return None, None
