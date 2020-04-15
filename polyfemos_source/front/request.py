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
Collection of miscellanous functions

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import os

import flask

from polyfemos.util.messenger import messenger


def nones():
    """
    :rtype: set
    :return: set of values considered nones
    """
    return {None, "", "None"}


def filepath(filepath, extension, force=False):
    """
    Returns the filepath with the given extension if it exists.
    If not, check if the 'retro' version is available and returns that.
    If both are unavailable, returns an empty string.

    :type filepath: str
    :param filepath: original filepath without the extension
    :type extension: str
    :param extension: file extension, e.g. ``.stf``, ``.csv`` or ``.alert``
    :type force: bool
    :param force: If ``True``, returns filepath with the given extension and
        if it does not exist, returns an empty string.
    :rtype: str
    :return:
    """
    tempfilepath = filepath + extension
    if os.path.isfile(tempfilepath):
        return tempfilepath
    msg = "File \'{}\' does not exist.".format(tempfilepath)
    if not force:
        tempfilepath = filepath + ".retro" + extension
        if os.path.isfile(tempfilepath):
            return tempfilepath
        msg += "\nFile \'{}\' does not exist.".format(tempfilepath)
    messenger(msg, "R")
    return ""


def arguments(key):
    """
    Request URL parameter by ``key``, some input validation is made

    :type key: str
    :param key:
    :rtype: str
    :return:
    """
    arg = flask.request.args.get(key)
    if not arg or arg is None:
        return arg
    valids = "0123456789qwertyuiopasdfghjklzxcvbnm.-_%,;"
    arg = (a for a in arg if a.lower() in valids)
    return "".join(arg)


def argument(key, replacer=""):
    """
    Request URL parameter by ``key``.
    Calls function :func:`~polyfemos.front.request.arguments`

    :type key: str
    :param key:
    :type replacer: str, optional
    :param replacer: If none value argument is returned for ``key``,
        returns ``replacer``, defaults to empty string
    :rtype: str
    :return:
    """
    arg = arguments(key)
    if arg in nones():
        return replacer
    return arg


def cookie(key, invalid_value=None):
    """
    :type key: str
    :param key: name of the cookie
    :type invalid_value: anything, optional
    :param invalid_value: If the cookie with name ``key`` doesn't exist
        ``invalid_value`` is returned
    :rtype:
    :return: the value of the cookie
    """
    return flask.request.cookies.get(key, invalid_value)
