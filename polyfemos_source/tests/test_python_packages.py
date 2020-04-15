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
Checks if all packages required by polyfemos are installed.

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import sys
import importlib
import subprocess


def print_line(*args):
    """
    Prints given ``args``.
    """
    print("".join([str(a).rjust(15, " ") for a in args]))


def python_version(pkg, required):
    """
    :type pkg: str
    :param pkg: python name
    :type required: str
    :param required: python version which works with polyfemos
    :rtype: str, str, str
    :return: python name, installed python version, required python version
    """
    version = ".".join(map(str, sys.version_info[:3]))
    return pkg, version, required


def uwsgi_version(pkg, required):
    """
    :type pkg: str
    :param pkg: uwsgi name
    :type required: str
    :param required: uwsgi version which works with polyfemos
    :rtype: str, str, str
    :return: uwsgi name, installed uwsgi version, required uwsgi version
    """
    version = "NOT INSTALLED"
    try:
        command = ("uwsgi", "--version")
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        version, error = process.communicate()
        version = version.decode('ascii').strip()
    except FileNotFoundError:
        pass
    return pkg, version, required


def package_version(pkg, required):
    """
    :type pkg: str
    :param pkg: package name
    :type required: str
    :param required: version which works with polyfemos
    :rtype: str, str, str
    :return: package name, installed version, required version
    """
    version = "NOT INSTALLED"
    try:
        module = importlib.import_module(pkg, package=None)
        version = module.__version__
    except ImportError:
        pass
    return pkg, version, required


_packages = [
    [python_version, "python", "3.7.3"],
    [uwsgi_version, "uwsgi", "2.0.18"],
    [package_version, "obspy", "1.1.1"],
    [package_version, "numpy", "1.17.2"],
    [package_version, "scipy", "1.3.1"],
    [package_version, "pathos", "0.2.5"],
    [package_version, "sklearn", "0.21.3"],
    [package_version, "bokeh", "1.2.0"],
    [package_version, "flask", "1.0.3"],
    [package_version, "flask_wtf", "0.14.2"],
    [package_version, "jinja2", "2.10.3"],
    [package_version, "pyproj", "1.9.5.1"],
]


def main():
    """
    Checks if all packages required by polyfemos are installed.
    """
    print_line("", "version", "works with")
    for (f, pkg, req) in _packages:
        print_line(*f(pkg, req))


if __name__ == '__main__':
    main()
