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
Functions for printing and debugging

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import functools
import multiprocessing as mp


def debugger(func_):
    r"""
    A decorator for monitoring function calls and returns

    :type func\_: func
    :param func\_:
    :rtype: func
    :return:
    """
    @functools.wraps(func_)
    def wrapper(*args, **kwargs):
        messenger("> ENTERING function: {}".format(func_.__name__), "M")
        # messenger("args: " + args.__repr__(), "M")
        # messenger("kwargs: " + kwargs.__repr__(), "M")
        rv = func_(*args, **kwargs)
        messenger("< EXITING function: {}".format(func_.__name__), "M")
        return rv
    return wrapper


def messenger(msg, option, showpid=True, quiet=False, quit_if_error=True):
    """
    Every print command around the program should
    be called using this function.

    :type msg: str
    :param msg: The message to be printed
    :type option: str
    :param option: Choose a string the ``msg`` will start with
    :type showpid: bool, optional
    :param showpid: defaults to ``True``, useful if multiprocessing is used,
        Shows the PID of the process outputting the ``msg``
    :type quiet: bool, optional
    :param quiet: defaults to ``False``, if ``True`` prints only
        error messages
    :type quit_if_error: bool, optional
    :param quit_if_error: defaults to ``True``, program execution is
        terminated if error occurs
    """

    quiet = 0 if "E" in option else quiet
    if quiet:
        return

    options = {
        "M": "  ",  # Message
        "N": "",  # Null
        "R": "> ",  # Runflow
        "W": "  Warning: ",  # Warning
        "E": "  Error:   ",  # Error
        "F": "  Invalid filepath: ",
        "O": "",  # Other
        "B": "\n# ",  # NB
    }

    startstr = options[option] if option in options else ""
    if showpid:
        pid = mp.current_process().pid
        startstr = "{0}pid-{1} ".format(startstr, str(pid))

    if "E" in option:
        print()

    for i, str_ in enumerate(msg.split("\n")):
        startstr = " " * len(startstr) if i else startstr
        print(startstr + str(str_))

    if "E" in option:
        print()
        if quit_if_error:
            quit()
