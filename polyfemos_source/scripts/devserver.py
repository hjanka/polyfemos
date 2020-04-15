#!/usr/bin/env python3
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
A command line script to create polyfemos development server,
call the script in folder where 'conf/front/global_config.yml'
is available.

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
from argparse import ArgumentParser

from polyfemos.front import main as pfm


def main(argv=None):
    """
    :type argv: list
    :param argv: command line arguments
    """
    parser = ArgumentParser(prog='polyfemos-devserver',
                            description=__doc__.strip())
    parser.add_argument('--host', type=str, default="127.0.0.1",
                        help='The host IP address, defaults to "127.0.0.1 '
                        '(local)"')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port, defaults to "5000"')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Switch on the debug mode')
    args = parser.parse_args(argv)
    pfm.app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        threaded=True)


if __name__ == "__main__":
    main()
