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
Timing utility classes for debugging

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import time
import functools


class Timer(object):
    """
    Timer class
    """
    def __init__(self, name=""):
        self.reset()
        self.name = name

    def reset(self):
        self.time = 0.
        self.t0 = 0.

    def start(self):
        self.t0 = time.time()
        return self

    def stop(self):
        self.lap(print_=False)
        self.t0 = 0

    def lap(self, print_=True, msg=""):
        if self.t0:
            self.time += time.time() - self.t0
        self.t0 = time.time()
        if print_:
            print(self, msg)

    def __str__(self):
        return "-- timer {:>15} {:.4f}".format(self.name, self.time / 1.)


class Timers(object):
    """
    A class to handle multiple timers
    """
    def __init__(self, N):
        for i in range(N):
            self.__dict__[i] = Timer()

    def start(self, n):
        self.__dict__[n].start()

    def stop(self, n):
        self.__dict__[n].stop()

    def __getitem__(self, k):
        return self.__dict__[k]

    def __setitem__(self, k, v):
        self.__dict__[k] = v

    def __str__(self):
        str_ = ""
        for v in self.__dict__.values():
            str_ += "{}\n".format(str(v))
        return str_


def timed(timer):
    """
    :type timer: :class:`~polyfemos.almanac.timer.Timer`
    :param timer: a timer to be used to time the decorated function
    :rtype: func
    :return: a decorator to time function execution
    """
    def decorator(func_):
        timer.name = func_.__name__
        @functools.wraps(func_)
        def wrapper(*args, **kwargs):
            timer.start()
            result = func_(*args, **kwargs)
            timer.lap()
            timer.stop()
            timer.reset()
            return result
        return wrapper
    return decorator
