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
Backend of polyfemos

- reading data and state of health miniseeds and log files
- writing state of health meta files
    - stf
    - csv
    - alert
- Creating data coverage plots
- Plotting PPSD plots (not yet)
- Triggering seismic events + Beampacking (not yet)

The program is used by creating '\*.conf' files which define the
program flow and values used.

See :ref:`Backend` for documentation.

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import sys
import time

from argparse import ArgumentParser

from polyfemos.util.messenger import messenger
from polyfemos.back import interpreter


def main(conffile):
    """
    :type conffile: str
    :param conffile: Filepath of the conffile
    """
    t0 = time.time()

    interp = interpreter.Interpreter()
    interp.readfile(conffile)

    interp.stop()

    t1 = time.time() - t0
    messenger(str(t1), "N", showpid=False)


def readconf(argv=None):
    r"""
    A function for reading '\*.conf' files from command line.

    :type argv: list
    :param argv: command line arguments
    """
    parser = ArgumentParser(prog='polyfemos-readconf',
                            description='A script for reading "*.conf" '
                                        'files from command line')
    parser.add_argument('conffile', type=str,
                        help='Polyfemos backend configuration file')
    args = parser.parse_args(argv)
    main(args.conffile)


if __name__ == "__main__":
    readconf(sys.argv)
