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
r"""
Contains all commands, special characters and reserved variables
for '\*.conf' files

.. data:: SYMBOLS

.. data:: CMDS

.. data:: VARS

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""

SYMBOLS = {
    "COMMENT": "#",
    "CMD": "\\",
    "VAR": "$",
    "RESVAR": "&",
}
CMDS = {
    "IMPORT": "{}IMPORT".format(SYMBOLS["CMD"]),
    "FLAG": "{}FLAG".format(SYMBOLS["CMD"]),
    "VAR": "{}VAR".format(SYMBOLS["CMD"]),
    "END": "{}END".format(SYMBOLS["CMD"]),
    "START": "{}START".format(SYMBOLS["CMD"]),
    "STOP": "{}STOP".format(SYMBOLS["CMD"]),
    "RUN": "{}RUN".format(SYMBOLS["CMD"]),
    "STATION": "{}STATION".format(SYMBOLS["CMD"]),
    "PAR": "{}PAR".format(SYMBOLS["CMD"]),
}
VARS = {
    "TODAY": "{}TODAY".format(SYMBOLS["RESVAR"]),
    "YEAR": "{}YEAR".format(SYMBOLS["RESVAR"]),
    "JULDAY": "{}JULDAY".format(SYMBOLS["RESVAR"]),
    "JULDAY_ZP": "{}JULDAY_ZP".format(SYMBOLS["RESVAR"]),
    "NETWORK": "{}NETWORK".format(SYMBOLS["RESVAR"]),
    "STATION": "{}STATION".format(SYMBOLS["RESVAR"]),
    "LOCATION": "{}LOCATION".format(SYMBOLS["RESVAR"]),
    "CHANNEL": "{}CHANNEL".format(SYMBOLS["RESVAR"]),
    "PARNAME": "{}PARNAME".format(SYMBOLS["RESVAR"]),
}
