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
Functions representing types used internally in polyfemos

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import math
import functools
import ast

from obspy import UTCDateTime

from polyfemos.parser import resources, functionparser, filepathparser
from polyfemos.almanac.ordinal import Ordinal


def check_type(func_, invalid_value=None):
    r"""
    A decorator to be composed with function where ``ValueError``
    or ``TypeError`` might occur.
    If the error occurs while ``func_`` is called, the return value of the
    ``func_`` is ``None``.

    :type func\_: func
    :param func\_:
    :type invalid_value: anything, optional
    :param invalid_value: If the type conversion is not possible, given invalid
        value is returned, defaults to ``None``.
    :rtype: func
    :return: ``wrapper``
    """
    @functools.wraps(func_)
    def wrapper(*args):
        try:
            return func_(*args)
        except (ValueError, TypeError):
            return invalid_value
    return wrapper


def literal_eval(inputstr, type_):
    """
    :type inputstr: str
    :param inputstr: a string representation of the value to be passed to
        :func:`ast.literal_eval`.
    :type type\_: class or type
    :param type\_: desired type of the resulting value
    :rtype: anything
    :return: The retrun type is ``type_``.
        Returns ``None`` if something went wrong while trying to
        convert ``inputstr`` into it's desired type.
    """
    try:
        return_value = ast.literal_eval(inputstr)
    except (SyntaxError, ValueError):
        return None
    if not isinstance(return_value, type_):
        return None
    return return_value


##
# Lists
###


def list_(inputstr, type_):
    """
    A list may be defined with square brackets or the brackets may be omitted.
    Note that, the whitespaces are treated literally and empty list entries
    are removed.

    :type inputstr: str
    :param inputstr: a string representation of a list containing either
        string, int, or float values.
    :type type\_: str
    :param type\_: Either 'str', 'float' or 'int', describing the resulting
        type of the list entries.
    :rtype: list
    :return: A list of either string, int, or float values.
    """
    inputstr = inputstr.strip("[]").split(",")
    inputstr = [s for s in inputstr if s]
    if type_ == "str" or len(inputstr) < 1:
        return inputstr
    _dict = {
        "int": (None, int_),
        "float": (float('nan'), float_),
    }
    if type_ not in _dict:
        return None
    # None to NaN in floatlist
    # None to None in intlist
    replacer, func_ = _dict[type_]
    inputstr = (func_(s) for s in inputstr)
    return [replacer if s is None else s for s in inputstr]


def intlist(inputstr):
    """
    :type inputstr: str
    :param inputstr: a string representation of a list containing integer
        values
    :rtype: list
    :return: A list of integer values
    """
    return list_(inputstr, "int")


def floatlist(inputstr):
    """
    :type inputstr: str
    :param inputstr: a string representation of a list containing floating
        point values
    :rtype: list
    :return: A list of float values
    """
    return list_(inputstr, "float")


def strlist(inputstr):
    """
    :type inputstr: str
    :param inputstr: a string representation of a list containing string
        values, for example: ``[1,asd,3, 4]``. The resulting list will
        be ``["1", "asd", "3", " 4"]``.
    :rtype: list
    :return: A list of string values
    """
    return list_(inputstr, "str")


###
# Specials
###


def var(inputstr):
    """
    :type inputstr: str
    :param inputstr:
    :rtype: str
    :return: Adds the variable symbol to the start of the ``inputstr``, if the
        ``inputstr`` lacks it.
    """
    if inputstr[0] != resources.SYMBOLS["VAR"]:
        inputstr = resources.SYMBOLS["VAR"] + inputstr
    return inputstr


def function(inputstr):
    """
    See the function syntax and more info in
    :func:`~polyfemos.parser.functionparser.function_from_str`

    :type inputstr: str
    :param inputstr: A string representing a function
    :rtype: func
    :return:
    """
    return functionparser.function_from_str(inputstr)


def filepath(inputstr):
    """
    see :func:`~polyfemos.parser.filepathparser.path_from_str` for more info.

    :type inputstr: str
    :param inputstr: A string representing a filepath, reserved variables
        may be used to create mutable filepaths.
    :rtype: func
    :return:
    """
    return filepathparser.path_from_str(inputstr)


def staticfilepath(inputstr):
    """
    see :func:`~polyfemos.parser.filepathparser.path_from_str` for more info.

    :type inputstr: str
    :param inputstr: A string representing a filepath, the ``inputstr``
        may not contain reserved variables
    :rtype: str
    :return: A string representing a filepath
    """
    return filepath(inputstr)()


def _get_offset(inputstr):
    """
    :type inputstr: str
    :param inputstr:
    :rtype: int
    :return: An integer number after '+' symbol in ``inputstr``,
        negative or positive. For negative offsets, the ``inputstr`` has to
        be for example: ``SOMETHING+-5``.
    """
    offset = inputstr.split("+")[-1]
    return check_type(int, invalid_value=0)(offset)


def utcdatetime(inputstr, today=None):
    """
    :type inputstr: str
    :param inputstr: A string compatible with
        :class:`~obspy.core.utcdatetime.UTCDateTime` constructor.
        If symbol '+' is contained in ``inputstr``, an offset is
        applied to the returned value. The offset is an integer value
        representing days. If the ``inputstr`` is not string type, the value
        is passed to :class:`~obspy.core.utcdatetime.UTCDateTime` constructor
        as is.
    :type today: :class:`~obspy.core.utcdatetime.UTCDateTime`, optional
    :param today: defaults to ``None``, if proper ``today`` is given,
        'TODAY' reserved variable is replaced with the given value.
    :rtype: :class:`~obspy.core.utcdatetime.UTCDateTime`
    :return:
    """
    if isinstance(inputstr, str) and \
            inputstr.startswith(resources.VARS["TODAY"]):
        offset = _get_offset(inputstr)
        if today is None:
            today = UTCDateTime()
        return today + offset * 86400
    return check_type(UTCDateTime)(inputstr)


def ordinal(inputstr, today=None):
    """
    :type inputstr: str
    :param inputstr: A string compatible with
        :class:`~polyfemos.almanac.ordinal.Ordinal` constructor.
        If symbol '+' is contained in ``inputstr``, an offset is
        applied to the returned value. The offset is an integer value
        representing days.
    :type today: :class:`~obspy.core.utcdatetime.UTCDateTime`, optional
    :param today: defaults to ``None``, if proper ``today`` is given,
        'TODAY' reserved variable is replaced with the given value.
    :rtype: :class:`~polyfemos.almanac.ordinal.Ordinal`
    :return:
    """
    if isinstance(inputstr, str):
        if inputstr.startswith(resources.VARS["TODAY"]):
            offset = _get_offset(inputstr)
            return Ordinal(today).shiftdays(offset)
        if inputstr.count("-") == 1:
            # for example inputstr 2019-3 is changed into 2019-003
            inputstr = "{}-{:0>3}".format(*inputstr.split("-"))
    elif isinstance(inputstr, Ordinal):
        return inputstr
    return Ordinal(inputstr)


def dict_(inputstr):
    """
    Calls :func:`~polyfemos.parser.typeoperator.literal_eval`
    to for a dictionary from ``inputstr`` and returns the dictionary.

    :type inputstr: str
    :param inputstr: A string representation of a python dictionary
    :rtype: dict
    :return: Dictionary or ``None``
    """
    return literal_eval(inputstr, dict)


###
# Basics
###


def str_(inputstr, check_empty=False):
    """
    :type inputstr: str
    :param inputstr:
    :rtype: str
    :return: ``inputstr`` converted into string, but nothing happened!
    """
    if check_empty and not inputstr:
        return None
    return inputstr


def float_(inputstr):
    """
    :type inputstr: str
    :param inputstr:
    :rtype: float
    :return: ``inputstr`` converted into float
    """
    if isinstance(inputstr, str):
        if isStrNaN(inputstr):
            return getNaN()
    return check_type(float)(inputstr)


@check_type
def int_(inputstr, to_float_first=True):
    """
    :type inputstr: str
    :param inputstr:
    :type to_float_first: bool, optional
    :param to_float_first: defaults to ``True``, If ``True`` the input string
        is first converted to float and then to integer.
    :rtype: int
    :return: ``inputstr`` converted into integer
    """
    if to_float_first:
        inputstr = float(inputstr)
    return int(inputstr)


def bool_(inputstr):
    """
    :type inputstr: str
    :param inputstr:
    :rtype: bool
    :return: ``inputstr`` converted into boolean, values ``True`` and
        ``False`` follow the boolean rules of python, e.g. ``"" = 0 = False``
        and ``"asd" = 1 = 9. = True``.
    """
    inputstr = ast.literal_eval(inputstr)
    return bool(inputstr)


def anything(inputstr):
    """
    Has no effect whatsoever.

    :type inputstr: str
    :param inputstr:
    :rtype: str
    :return:
    """
    return inputstr


def getNaN():
    """
    :rtype: float
    :return: ``float('nan')``
    """
    return float('nan')


def isNaN(num):
    """
    check if ``num`` is NaN

    :type num: numlike
    :param num:
    :rtype: bool
    :return:
    """
    return math.isnan(num)


def strNaN():
    """
    :rtype: str
    :return: string representation of NaN
    """
    return "NaN"


def isStrNaN(inputstr):
    r"""
    :type inputstr: str
    :param inputstr:
    :rtype: bool
    :return: ``True``, if ``inputstr`` is is equal any string representation of
        nan.
    """
    if not isinstance(inputstr, str):
        return False
    return inputstr.lower() == "nan"


def replaceNaN(func_):
    r"""
    A decorator to replace NaN (see
    :func:`~polyfemos.parser.typeoperator.isStrNaN`)
    values of ``args`` and ``kwargs``  of ``func_`` with an empty string.

    :type func\_: func
    :param func\_:
    :rtype: func
    :return: ``wrapper``
    """
    @functools.wraps(func_)
    def wrapper(*args, **kwargs):
        args = ["" if isStrNaN(v) else v for v in args]
        kwargs = {k: "" if isStrNaN(v) else v for k, v in kwargs.items()}
        return func_(*args, **kwargs)
    return wrapper


def NaN2None(func_):
    r"""
    A decorator to be composed with a one-argument function,
    If the argument of the decorated function (``func_``) is NaN
    return ``None``, else call function ``func_``

    :type func\_: func
    :param func\_: A one-argument function
    :rtype: func
    :return: ``wrapper``
    """
    @functools.wraps(func_)
    def wrapper(x):
        if isNaN(x):
            return None
        return func_(x)
    return wrapper
