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
Classes for handling datapoints

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import sys
from dateutil import tz
import math
import functools

import numpy as np

from polyfemos.parser import typeoperator as to
from polyfemos.util.messenger import messenger


def remove_timezone_other(dt):
    """
    :type dt: :class:`~datetime.datetime`
    :param dt:
    :rtype: :class:`~datetime.datetime`
    :return: a datetime instance without timezone
    """
    # Atleast with Python 3.5 and 3.7 The next line works
    dt = dt.replace(tzinfo=tz.gettz('UTC'))
    return dt.replace(tzinfo=None)


def remove_timezone_py36(dt):
    """
    Used with python 3.6

    :type dt: :class:`~datetime.datetime`
    :param dt:
    :rtype: :class:`~datetime.datetime`
    :return: a datetime instance without timezone
    """
    dt = dt.replace(tzinfo=tz.gettz('UTC'))
    return dt.astimezone(tz.tzlocal()).replace(tzinfo=None)


def remove_timezone_py37(dt):
    """
    :type dt: :class:`~datetime.datetime`
    :param dt:
    :rtype: :class:`~datetime.datetime`
    :return: the function does nothing to the datetime object
    """
    return dt


_timezone_removal_functions = {
    "3.6": remove_timezone_py36,
    "3.7": remove_timezone_py37,
}

# Bokeh has complications with different python version
python_version = ".".join(map(str, sys.version_info[:2]))
remove_timezone = remove_timezone_other
if python_version in _timezone_removal_functions:
    remove_timezone = _timezone_removal_functions[python_version]


def _track_datalen(method):
    """
    A decorator to be used with
    :class:`~polyfemos.front.sohplot.datacontainer.DataContainer`
    to keep track of the
    datapoint amount and quantity of nan values. At the moment the
    looping of the datapoints is not very optimized.

    :type method: func
    :param method: A decorated method
    :rtype: func
    :return:
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.track_datalen:
            msg = "in method: {}".format(method.__name__)
            messenger(msg, "R")
            orig_len = len(self)
            orig_nan_len = self.count_nans()
        method(self, *args, **kwargs)
        if self.track_datalen:
            new_len = len(self)
            new_nan_len = self.count_nans()
            str_ = "{:*<19}**".format(method.__name__ + ":")
            str_ += "dps:*{:*>7}*>*{:*<7}*".format(orig_len, new_len)
            str_ += "nans:*{:*>7}*>*{:*<7}".format(orig_nan_len, new_nan_len)
            self.add2info(str_)
    return wrapper


class DataPoint(object):
    """
    A structlike class to store one datapoint in timeseries data
    """
    def __init__(self, dtstr=None, timestamp=None, utcdatetime=None,
                 y=None, z=None):
        """
        The data must have timevalue, given either ``dtstr``, ``timestamp``
        or ``utcdatetime``.
        ``z`` is an optional axis containing arbitrary string values following
        python dictionary syntax

        :type dtstr: str
        :param dtstr: utcdatetime compatible string representing time value
        :type timestamp: float
        :param timestamp:
        :type utcdatetime: :class:`~obspy.core.utcdatetime.UTCDateTime`
        :param utcdatetime:
        :type y: str or numlike
        :param y: string representing float number, if invalid string is
            provided, ``y`` will be ``nan``
        :type z: str, optional
        :param z: Additional arbitrary values contained in string following
            python dict syntax
        """
        self.__dtstr = dtstr
        self.__timestamp = timestamp

        self.__utcdatetime = utcdatetime

        self.__datetime = None
        self.__ordinal = None
        self.__timezone_naive_datetime = None

        self.__hash = None

        self.z = z
        self.y = to.check_type(float, invalid_value=float('nan'))(y)

    def get_utcdatetime(self):
        """
        If ``self.__utcdatetime`` is not previously defined,
        the value is read using ``self.__dtstr`` or
        ``self.__timestamp``. If either of those is not provided,
        error is thrown.

        :rtype: :class:`~obspy.core.utcdatetime.UTCDateTime`
        :return:
        """
        if self.__utcdatetime is not None:
            return self.__utcdatetime
        if self.__dtstr is not None:
            self.__utcdatetime = to.utcdatetime(self.__dtstr)
        elif self.__timestamp is not None:
            self.__utcdatetime = to.utcdatetime(self.__timestamp)
        if self.__utcdatetime is None:
            raise Exception("DataPoint has no valid timevalue")
        return self.__utcdatetime

    def get_dtstr(self):
        """
        :rtype: str
        :return: string representation of the timevalue
        """
        if self.__dtstr is None:
            self.__dtstr = str(self.get_utcdatetime())
        return self.__dtstr

    def get_timestamp(self):
        """
        :rtype: float
        :return: timestamp
        """
        if self.__timestamp is None:
            self.__timestamp = self.get_utcdatetime().timestamp
        return self.__timestamp

    def get_datetime(self):
        """
        :rtype: :class:`~datetime.datetime`
        :return:
        """
        if self.__datetime is None:
            self.__datetime = self.get_utcdatetime().datetime
        return self.__datetime

    def get_ordinal(self):
        """
        :rtype: str
        :return: year and the day of the yeat as a string in format
            ``YEAR.JULDAY``, e.g. ``2019.023``
        """
        if self.__ordinal is None:
            self.__ordinal = self.get_utcdatetime().strftime("%Y.%j")
        return self.__ordinal

    def get_timezone_naive_datetime(self):
        """
        :rtype: :class:`~datetime.datetime`
        :return:
        """
        if self.__timezone_naive_datetime is not None:
            return self.__timezone_naive_datetime
        self.__timezone_naive_datetime = remove_timezone(self.get_datetime())
        return self.__timezone_naive_datetime

    def set_z(self, value):
        """
        :type value: str
        :param value: Value to be set to ``z`` attribute
        """
        self.z = value

    def get_z(self):
        """
        :rtype: dict
        :return: Returns the value of ``z`` attribute. If the type was not
            previously converted from string to dictionary, the conversion
            is done in addition.
        """
        if isinstance(self.z, str):
            self.z = to.dict_(self.z)
        return self.z

    def ifz(self):
        """
        :rtype: bool
        :return: return ``True`` if ``z`` has a value set
        """
        return self.z is not None

    def isnan(self):
        """
        :rtype: bool
        :return: Checks if ``y`` is nan
        """
        return math.isnan(self.y)

    def isnotnan(self):
        """
        :rtype: bool
        :return: return ``True`` if ``y`` is not nan
        """
        return not self.isnan()

    def tonan(self, inplace=True):
        """
        Change the ``y`` attribute to nan. If ``inplace`` is ``False``, a
        copy of :class:`~polyfemos.front.sohplot.datacontainer.DataPoint`
        is returned. Note the mutability of the
        :class:`~polyfemos.front.sohplot.datacontainer.DataPoint`
        instance if ``inplace`` is ``True``.

        :type inplace: bool, optional
        :param inplace: defaults to ``True``
        :rtype: :class:`~polyfemos.front.sohplot.datacontainer.DataPoint`
        :return:
        """
        if inplace:
            self.y = float('nan')
            return self
        return self.copy().tonan()

    def copy(self):
        """
        :rtype: :class:`~polyfemos.front.sohplot.datacontainer.DataPoint`
        :return: returs a copy of the current
            :class:`~polyfemos.front.sohplot.datacontainer.DataPoint` instance
        """
        return DataPoint(timestamp=self.__timestamp, dtstr=self.__dtstr,
                         utcdatetime=self.__utcdatetime, y=self.y, z=self.z)

    def __str__(self):
        """
        :rtype: str
        :return: A some kind of string representation of the values
        """
        return "{} {} {}".format(
            self.get_dtstr(), self.get_timestamp(), self.y, self.z)

    def __bool__(self):
        """
        :rtype: bool
        :return: returns ``True`` if ``y`` is not nan
        """
        return self.isnotnan()

    def __eq__(self, other):
        """
        Compares the timestamp and y values between ``self`` and ``other``.
        If both values are iedntical, returns ``True``.

        :type other: :class:`~polyfemos.front.sohplot.datacontainer.DataPoint`
        :param other:
        :rtype: bool
        :return:
        """
        if self.get_timestamp() == other.get_timestamp():
            if self.isnan() and other.isnan():
                return True
            elif self.y == other.y:
                return True
        return False

    def __ne__(self, other):
        """
        :type other: :class:`~polyfemos.front.sohplot.datacontainer.DataPoint`
        :param other:
        :rtype: bool
        :return: opposite of the
            :meth:`~polyfemos.front.sohplot.datacontainer.DataPoint.__eq__`
        """
        return not self == other

    def __hash__(self):
        """
        :rtype: int
        :return: hashed tuple containing ``self.__timestamp`` and
            ``self.y`` values
        """
        if self.__hash is None:
            self.__hash = hash((self.get_timestamp(), self.y))
        return self.__hash


class DataContainer(object):
    """
    A class to handle timeseries data consisting of
    :class:`~polyfemos.front.sohplot.datacontainer.DataPoint` instances.

    The class has ``__setitem__`` and ``__getitem__`` methods so it works like
    dictionary on that part.
    """
    def __init__(self, track_datalen=False, remove_identicals=False):
        """
        :type track_datalen: bool, optional
        :param track_datalen: Defaults to ``False``, If ``True``, the amount
            of datapoints, nans, etc., is monitored.
        :type remove_identicals: bool, optional
        :param remove_identicals: defaults to ``False``. If ``True``,
            values with identical x and y values are removed.
        """
        self.track_datalen = track_datalen
        self.remove_identicals = remove_identicals
        # A list containing DataPoint instances
        self.datapoints = []
        # After advanced outlier removal, this list contains the outlier
        # datapoints
        self.outlier_datapoints = []

        self.__ys_wo_nans = []
        self.__info = []

        self.__added_datapoint_hashes = set()
        self.__identical_count = 0

    def add2info(self, str_):
        r"""
        :type str\_: str
        :param str\_: A notes appended to ``self.__info`` list
        """
        self.__info.append(str_)

    def get_info(self):
        """
        :rtype: list
        :return: A list containing the info notes
        """
        return self.__info

    def append(self, dp):
        """
        If ``self.remove_identicals`` is ``True``,
        the datapoint is not included if it has identical x and y values
        as one of the already added datapoints.

        :type value: :class:`~polyfemos.front.sohplot.datacontainer.DataPoint`
        :param value: Addends
            :class:`~polyfemos.front.sohplot.datacontainer.DataPoint`
            instance to ``self.datapoints``
        """
        if self.remove_identicals:
            dphash = hash(dp)
            if dphash not in self.__added_datapoint_hashes:
                self.datapoints.append(dp)
                self.__added_datapoint_hashes.add(dphash)
            else:
                self.__identical_count += 1
        else:
            self.datapoints.append(dp)

    def sort(self):
        """
        Sorts ``self.datapoints`` comparing timestamp values
        """
        self.datapoints = \
            sorted(self.datapoints, key=lambda dp: dp.get_timestamp())

    def add_identical_removal_info(self):
        """
        Adds original datapoint and nan amounts and identical datapoint
        information to ``self.__info``.
        """
        if self.track_datalen:
            str_ = ""
            str_ += "dps:*{:*<7}* nans:*{:*<7}*" \
                .format(len(self), self.count_nans())
            str_ += "identicals removed:*{:*<7}*" \
                .format(self.__identical_count)
            self.add2info(str_)

    @_track_datalen
    def remove_irrationals(self, irlims=None):
        """
        If :class:`~polyfemos.front.sohplot.datacontainer.DataPoint`
        instance's ``y`` value is not within the interval
        (including both ends) defined by ``irlims``, the ``y``
        is set to nan in place.

        :type irlims: list
        :param irlims: lower and upper limit for irrational values
        """
        if irlims is None or len(irlims) != 2:
            return
        irlims = sorted(irlims)

        for dp in self.datapoints:
            if irlims[0] <= dp.y <= irlims[1] or dp.isnan():
                pass
            else:
                dp.tonan()

    @_track_datalen
    def outlier_removal(self, outlierremfunc):
        """
        Applies advanced outlier removal to ``datapoints`` attribute.
        Changes ``y`` values of outlying datapoints into nan, while
        simultaneously creating dataset ``self.outlier_datapoints``,
        which contains the outliers.

        Some functions for removing outliers are in
        :mod:`~polyfemos.data.outlierremover`.

        :type outlierremfunc: func
        :param outlierremfunc: a function to remove outliers, arguments of the
            ``outlierremfunc`` has to be predefined, except the actual data.
        """
        # If outlierremfunc is not a function, do nothing
        if not callable(outlierremfunc):
            return

        if len(self) <= 1:
            return

        tempdata = np.array([
            [dp.get_timestamp(), dp.y] for dp in self.datapoints
        ])

        mask = outlierremfunc(tempdata)

        self.outlier_datapoints = []
        for m, dp in zip(mask, self.datapoints):
            copydp = dp.copy()
            if math.isnan(m):
                dp.tonan()
                self.outlier_datapoints.append(copydp.tonan())
            elif m:
                self.outlier_datapoints.append(copydp.tonan())
            else:
                self.outlier_datapoints.append(copydp)
                dp.tonan()

    @_track_datalen
    def decimate(self):
        """
        Decimates ``self.datapoints`` list by removing datapoints so that
        the after decimation, the amount of datapoints in the list is not over
        ``decimation_limit``, which is set to 10000.

        Bokeh can plot 10000 datapoints with relative ease but
        more datapoints than that will result in slow plotting.
        """
        decimation_limit = 10000.0
        orig_len = len(self)

        if orig_len >= decimation_limit:
            decimation_factor = math.ceil(orig_len / decimation_limit)
            self.datapoints = self.datapoints[::decimation_factor]

    def get_ys_wo_nans(self, force=False):
        """
        :type force: bool, optional
        :param force: defaults to ``False``, if ``True`` the returned list
            is recalculated in every case.
        :rtype: list
        :return: A list containing ``y`` values of
            :class:`~polyfemos.front.sohplot.datacontainer.DataPoint`
            instances excluding nan values
        """
        if len(self.__ys_wo_nans) < 1 or force:
            self.__ys_wo_nans = [dp.y for dp in self.datapoints if dp]
        return self.__ys_wo_nans

    def count_nans(self):
        """
        :rtype: int
        :return: A count of nan values in ``self.datapoints`` list
        """
        return sum(1 for dp in self.datapoints if not dp)

    def __len__(self):
        """
        :rtype: int
        :return: length of ``self.datapoints``
        """
        return len(self.datapoints)
