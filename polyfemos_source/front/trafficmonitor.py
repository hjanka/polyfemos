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
Monitors and limits website usage

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
# Daisy, Daisy, give me your answer do.
# I'm half crazy all for the love of you.
# It won't be a stylish marriage,
# I can't afford a carriage.
# But you'll look sweet upon the seat
# Of a bicycle built for two.
import functools

import flask
from obspy import UTCDateTime

from polyfemos.util import fileutils
from polyfemos.front import userdef, request, colors


class IPStorage():
    """
    A class which handles IP addresses of the users

    Every instance of the class uses the same file to save the IP addresses.
    """
    def __init__(self):
        """
        Clears the ipstorage file
        """
        self.__file = ".ipstorage.txt"
        self.clear()

    def write(self, str_):
        r"""
        :type str\_: str
        :param str\_: A string to be written into the ipstorage file
        """
        fileutils.write_file(self.__file, str_, cmf=False)

    def clear(self):
        """
        Clears the ipstorage file
        """
        self.write("")

    def append(self, str_):
        r"""
        :type str\_: str
        :param str\_: A string to be appended into the ipstorage file
        """
        fileutils.write_file(self.__file, str_, mode="a", cmf=False)

    def add(self, ip):
        """
        :type ip: str
        :param ip: IP address to be added to the ipstorage
        """
        if self.has_ip(ip):
            return
        self.append(ip + "\n")

    def has_ip(self, ip):
        """
        :type ip: str
        :param ip: IP address
        :rtype: bool
        :return: ``True`` if ipstorage has the given ``ip``
        """
        return ip in self

    def remove(self, ip):
        """
        :type ip: str
        :param ip: an IP address to be removed from the ipstorage
        """
        str_ = ""
        for stored_ip in self:
            if ip != stored_ip:
                str_ += stored_ip + "\n"
        self.write(str_)

    def __iter__(self):
        """
        :rtype: generator
        :return: all IP addresses stored in the ipstrorage file
        """
        rows = fileutils.read_file(self.__file)
        return (row.strip("\n") for row in rows)

    def __str__(self):
        """
        :rtype: str
        :return: A list of all IP addresses stored in the ipstorage file.
        """
        return ", ".join(r for r in self)


def gip():
    """
    :rtype: str
    :return: IP address of the user
    """
    if flask.request.headers.getlist("X-Forwarded-For"):
        ip = flask.request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = flask.request.remote_addr
    return str(ip)


def gun():
    """
    :rtype: str
    :return: Username of the user
    """
    if flask.request.authorization is None:
        return "-"
    else:
        return flask.request.authorization.username


def check_permission(access_level, limit_network=False):
    """
    The users and their access levels are defined in YAML config files.
    See :func:`~polyfemos.front.userdef.users` for more info.

    The local user (ip='127.0.0.1') has the maximum access level (1).
    An unidentified user will have the minimum access level (the function
    always returns ``False``).

    :type access_level: int
    :param access_level: requested access level
    :type limit_network: bool, optional
    :param limit_network: Defaults to ``False``. If ``True``, the allowed
        networks of the user are checked in addition to access level.
    :rtype: bool
    :return: Returns ``True`` if the users access level is smaller or
        equal to requested access level (``access_level``).
    """
    if gip() == "127.0.0.1":
        return True
    user = gun()
    users = userdef.users()
    if user not in users:
        return False
    if "access_level" not in users[user]:
        return False
    if limit_network:
        if "allowed_networks" not in users[user]:
            return False
        network_code = request.cookie("network_code")
        if network_code not in users[user]["allowed_networks"]:
            return False
    return users[user]["access_level"] <= access_level


def logged(func_):
    """
    A decorator used to log usage of the functions
    Logs the time, IP address and username of the user and the function
    (``func_``) used.

    :type func\_: func
    :param func\_:
    :rtype: func
    :return:
    """
    @functools.wraps(func_)
    def wrapper(*args, **kwargs):
        ip = gip()
        username = gun()
        time = UTCDateTime.now().strftime("%Y-%m-%dT%H:%M:%S+0000Z")
        functionname = func_.__name__
        str_ = "{:30} {:25} {:25} {:25}\n" \
            .format(time, ip, username, functionname)
        fn = userdef.paths("webusagelog_file")
        fileutils.write_file(fn, str_, mode="a", cmf=False)
        return func_(*args, **kwargs)
    return wrapper


def limited(ipstorage):
    """
    A function call limiter.
    The functions with limited decorator
    may only be called one at the time per IP address.
    Use as a decorator with arguments. This applies to users with
    access level equal or more than 2.

    The access level check made by calling
    :func:`~polyfemos.front.trafficmonitor.check_permission`.

    :type ipstorage: :class:`~polyfemos.front.trafficmonitor.IPStorage`
    :param ipstorage:
    :rtype: func
    :return: A decorator using
        :class:`~polyfemos.front.trafficmonitor.IPStorage`
    """
    def decorator(func_):
        @functools.wraps(func_)
        def wrapper(*args, **kwargs):
            ip = gip()
            if check_permission(1):
                return func_(*args, **kwargs)
            elif ip in ipstorage:
                str_ = "You ({}) already have an execution underway." \
                    .format(ip)
                return colors.colored_template("message.htm", text=str_)
            else:
                ipstorage.add(ip)
                return_ = func_(*args, **kwargs)
                ipstorage.remove(ip)
                return return_
        return wrapper
    return decorator


def limit_access(access_level=2, limit_network=True):
    r"""
    A decorator used limit access of users. Users with
    access level equal or greater than 3 are not permitted to enter the site.

    The access level check made by calling
    :func:`~polyfemos.front.trafficmonitor.check_permission`.

    :type access_level: int, optional
    :param access_level: requested access level, defaults to ``2``
    :type limit_network: bool, optional
    :param limit_network: Defaults to ``True``. If ``True``, the allowed
        networks of the user are checked in addition to access level.
    :rtype: func
    :return: a decorator to limit access
    """
    def decorator(func_):
        @functools.wraps(func_)
        def wrapper(*args, **kwargs):
            if not check_permission(access_level, limit_network=limit_network):
                str_ = "You don't have access to this site."
                return colors.colored_template("message.htm", text=str_)
            return func_(*args, **kwargs)
        return wrapper
    return decorator
