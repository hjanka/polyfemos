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
Contains :class:`~polyfemos.back.parameter.Parameter` class

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import itertools

from polyfemos.parser import typeoperator as to


class Parameter(object):
    """
    A state of health parameter class
    """
    def __init__(self, class_="", name="", code="", decimation_factor=1,
                 scale=0., unit="", plotlims=[], priority=0, alertfunc=None,
                 irlims=[], alertlims=[], path=None):
        r"""
        :type class\_: str
        :param class\_: arbitrary string defining the class of the parameter
        :type name: str
        :param name: name of the parameter, e.g. 'Digitizer_input_voltage'
        :type code: str
        :param code: code of the parameter, e.g. 'HHZ.DCL'
        :type decimation_factor: int
        :param decimation_factor: The data of the parameter is decimated
            according to this value.
        :type scale: float
        :param scale: the data values of the parameter are with the given
            ``scale``
        :type unit: str
        :param unit: unit of the parameter values after scaling
        :type plotlims: list
        :param plotlims: list of two numbers, lower and higher limits
            for plotting
        :type priority: numlike
        :param priority: priority of the parameter, smaller numbers correspond
            to a higher priority
        :type alertfunc: func
        :param alertfunc: see
            :func:`~polyfemos.back.seismic.lumberjack.get_tibs` for more info
        :type irlims: list
        :param irlims: list of two numbers, lower and higher limit defining
            interval where the data values considered reasonable, the interval
            includes both endpoints.
        :type alertlims: list
        :param alertlims: a list (at most 6 entries) defining different alert
            stages, 3 entries for lower and higher limits.
            for example: ``[3,5,2,6,1,NaN]``,
            ``[red_lower, red_higher, yellow_lower, ...]``
        :type path: func
        :param path: A filepath function returning datafile paths for the
            parameter
        """
        self.class_ = class_
        self.name = name
        self.code = code

        self.channel_code, self.code_key = (code + ".").split(".")[:2]

        self.decimation_factor = int(max(decimation_factor, 1))
        self.scale = lambda x: scale * x
        self.unit = unit
        self.plotlims = plotlims
        self.priority = priority
        self.irlims = irlims
        self.alertlims = alertlims[:6]
        self.path = path

        self.create_alertfunc(alertfunc)

    def create_alertfunc(self, alertfunc):
        """
        The resulting class attribute ``self.alertfunc`` is decorated with
        :func:`~polyfemos.parser.typeoperator.NaN2None`

        :type alertfunc: func
        :param alertfunc: If ``alertfunc`` is ``None``, ``self.alertfunc``
            is set to always return ``False``
        """
        self.alertfunc = lambda x: False
        if alertfunc is not None:
            self.alertfunc = alertfunc
        self.alertfunc = to.NaN2None(self.alertfunc)

    def create_header_field(self, field):
        """
        :type field: str
        :param field:
        :rtype: str
        :return: a string combining the parameter name and the header field.
        """
        return "{}_{}".format(self.name, field)

    def generate_header(self):
        r"""
        :rtype: generator
        :return: A generator yielding '\*.stf' file header lines
        """
        yield self.create_header_field("UNIT"), [self.unit]
        yield self.create_header_field("PRIORITY"), [self.priority]
        yield self.create_header_field("PLOTLIMS"), self.plotlims
        yield self.create_header_field("IRLIMS"), self.irlims
        evens = self.alertlims[::2]
        odds = self.alertlims[1::2]
        limlist = ["RED", "ORANGE", "YELLOW"]
        for lims in itertools.zip_longest(evens, odds, fillvalue=to.getNaN()):
            yield self.create_header_field(limlist.pop()), lims

    def __getitem__(self, key):
        """
        :type key: str
        :param key: name of the class attribute
        :rtype:
        :return: value of the class attribute ``key``, if ``key``
            is not an attribute, return ``None``
        """
        if key not in self.__dict__:
            return None
        return self.__dict__[key]

    def __str__(self):
        """
        :rtype: str
        :return: somekind of string representation of the parameter
        """
        return "{:>20}{:>10}".format(self.name, self.code)
