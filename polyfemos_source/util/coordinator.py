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
Coordinate transformation functions

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import pyproj
import numpy as np
from scipy.interpolate import SmoothBivariateSpline

from polyfemos.util.messenger import messenger
from polyfemos.util import fileutils


def ddm2dd(degs, mins, letter):
    """
    :type degs: numlike
    :param degs: coordinate degrees
    :type mins: numlike
    :param mins: coordinate decimal minutes
    :type letter: str
    :param letter: ``N``, ``S``, ``E``, or ``W``
    :rtype: float
    :return: coordinate as decimal degrees
    """
    sign = [1, -1][letter in "SW"]
    decimaldegrees = sign * float(degs) + float(mins) / 60.
    return decimaldegrees


def transform_from_ozi_map(mapfile):
    """
    Reads `OziExplorer <https://www.oziexplorer4.com/w/>`_
    map files and returns a function to convert
    WGS84 coordinates to pixels.

    The map file can be created manually and it
    should contain at least the following mandatory lines:

    .. code-block:: text

        Point01,xy, 110, 159,in, deg, 68, 47.222,N, 22, 46.498,E, grid, , , , N
        Point02,xy, 219, 159,in, deg, 68, 50.001,N, 25, 32.324,E, grid, , , , N
        Point03,xy, 329, 159,in, deg, 68, 50.063,N, 28, 20.055,E, grid, , , , N
        Point04,xy, 110, 318,in, deg, 67, 19.826,N, 23, 2.020,E, grid, , , , N
        Point05,xy, 219, 318,in, deg, 67, 22.408,N, 25, 37.707,E, grid, , , , N
        Point06,xy, 329, 318,in, deg, 67, 22.466,N, 28, 15.139,E, grid, , , , N
        Point07,xy, 110, 476,in, deg, 65, 52.937,N, 23, 15.536,E, grid, , , , N
        Point08,xy, 219, 476,in, deg, 65, 55.346,N, 25, 42.393,E, grid, , , , N
        Point09,xy, 329, 476,in, deg, 65, 55.401,N, 28, 10.860,E, grid, , , , N

    .. code-block:: text

        MMPLL,1, 19.499680, 70.147437
        MMPLL,2, 31.374991, 70.251143
        MMPLL,3, 30.424810, 64.431702
        MMPLL,4, 21.120046, 64.353722

    Each line is treated as a list of elements separated with commas,
    whitespaces are removed.
    The 'Point' entries are used to create the conversion and
    the 'MMPLL' entries define the extrapolation area.
    In 'Point' entries indices 2 and 3 are pixel coordinates and
    indices from 6 to 11 are the corresponding WGS84 coordinates
    (indices 2 and 3 in the 'MMPLL' entry).

    Lines that do not start with either 'MMPLL' or 'Point' are skipped.

    :type mapfile: str
    :param mapfile: path to OziExplorer map file
    :rtype: func
    :return: A function taking WGS84 longitude and latitude as arguments
        and returning pixel xy-coordinates as a tuple.
    """
    points = []
    corners = []

    for row in fileutils.rowsof(mapfile, delims=", "):
        if len(row) >= 4 and row[0] == "MMPLL":
            corners.append([*map(float, row[2:4])])
        elif len(row) >= 12 and row[0].startswith("Point"):
            px, py = map(float, row[2:4])
            lon = ddm2dd(*row[9:12])
            lat = ddm2dd(*row[6:9])
            points.append([lon, lat, px, py])

    points = np.array(points)
    corners = np.array(corners)

    bx0, bx1 = np.min(corners[:, 0]), np.max(corners[:, 0])
    by0, by1 = np.min(corners[:, 1]), np.max(corners[:, 1])

    lons = points[:, 0]
    lats = points[:, 1]
    pxs = points[:, 2]
    pys = points[:, 3]

    sx = SmoothBivariateSpline(
        lons, lats, pxs, bbox=[bx0, bx1, by0, by1], kx=1, ky=1)
    sy = SmoothBivariateSpline(
        lons, lats, pys, bbox=[bx0, bx1, by0, by1], kx=1, ky=1)

    return lambda lon, lat: (sx(lon, lat), sy(lon, lat))


def get_transform(from_epsg, to_epsg):
    """
    :type from_epsg: str
    :param from_epsg: EPSG code of the original coordinate system
    :type to_epsg: str
    :param to_epsg: EPSG code of the resulting coordinate system
    :rtype: func
    :return: A coordinate transformation function taking xy-coordinates
        in ``from_epsg`` coordinate system and returning xy-coordinates in
        ``to_epsg`` coordinate system
    """
    try:
        from_coords = pyproj.Proj("+init=EPSG:{}".format(from_epsg))
        to_coords = pyproj.Proj("+init=EPSG:{}".format(to_epsg))
    except RuntimeError:
        msg = "No coordinate conversion available for ESPGs from " \
              "'{}' to '{}'.".format(from_epsg, to_epsg)
        messenger(msg, "W")
        return lambda x, y: (x, y)
    return lambda x, y: pyproj.transform(from_coords, to_coords, x, y)
