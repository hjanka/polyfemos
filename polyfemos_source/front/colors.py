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
Contains all color values for polyfemos

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import functools

from flask import render_template


WHITE = "#ffffff"
GREY_1 = "#fafafa"
GREY_2 = "#f5f5f5"
GREY_3 = "#dddddd"
GREY_4 = "#aaaaaa"
BLACK = "#000000"
RED_1 = "#ff4d88"
RED_2 = "#e60047"
RED_3 = "#990033"
ALERT_GREEN = "#82ff82"
ALERT_YELLOW = "#eeff88"
ALERT_RED = "#ff4d88"
GREEN = "#476b6b"
BLUE = "#22408f"


def get_color_styles():
    """
    :rtype: str
    :return: css styles consisting of color variables
    """
    str_ = ":root {\n"
    str_ += "  --white: {};\n".format(WHITE)
    str_ += "  --grey-1: {};\n".format(GREY_1)
    str_ += "  --grey-2: {};\n".format(GREY_2)
    str_ += "  --grey-3: {};\n".format(GREY_3)
    str_ += "  --grey-4: {};\n".format(GREY_4)
    str_ += "  --black: {};\n".format(BLACK)
    str_ += "  --red-1: {};\n".format(RED_1)
    str_ += "  --red-2: {};\n".format(RED_2)
    str_ += "  --red-3: {};\n".format(RED_3)
    str_ += "  --alert-green: {};\n".format(ALERT_GREEN)
    str_ += "  --alert-yellow: {};\n".format(ALERT_YELLOW)
    str_ += "  --alert-red: {};\n".format(ALERT_RED)
    str_ += "  --green: {};\n".format(GREEN)
    str_ += "  --blue: {};\n".format(BLUE)
    str_ += "}\n"
    return str_


def render_colors(func_):
    """
    :type func\_: func
    :param func\_: :func:`~flask.render_template`
    :rtype: func
    :return: decorated function
    """
    @functools.wraps(func_)
    def wrapper(*args, **kwargs):
        return func_(*args, color_styles=get_color_styles(), **kwargs)
    return wrapper


colored_template = render_colors(render_template)
