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
A command line script to check polyfemos output files.

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import os
import re
import itertools
import functools

from argparse import ArgumentParser

from polyfemos.util.messenger import messenger
from polyfemos.front.sohplot import outfilefields
from polyfemos.back import filewriter
from polyfemos.util import fileutils


def print_warning(filename, msg):
    """
    :type filename: str
    :param filename: path to a file where the error was encountered
    :type msg: str
    :param msg: Message to be printed, if empty, nothing is printed.
    """
    if msg:
        msg = "In file: {}\n{}".format(filename, msg).strip()
        messenger(msg, "W", showpid=False)


def check_header(header, valid_header):
    """
    Checks if two lists of strings are identical using using
    :func:`re.compile` and :func:`re.match` functions. Asterisk ('\*')
    can be used to match any number of any characters.

    :type header: list[str]
    :param header: The header which is tried to verify.
    :type valid_header: list[str]
    :param valid_header: A header which the given ``header`` is compared to.
    :rtype: str
    :return: Error message if given headers does not match. If an empty string
        is returned, the ``header`` is ok.
    """
    msg = ""
    zipped = itertools.zip_longest(header, valid_header, fillvalue="")
    for h1, h2 in zipped:
        pattern = h2
        pattern = pattern.replace(" ", "\ ")
        pattern = pattern.replace("*", ".*")
        pattern = pattern.replace("[", "\[")
        pattern = pattern.replace("]", "\]")
        pattern = re.compile("(?s:{})\Z".format(pattern))
        if not pattern.match(h1):
            msg += "Header field '{}' does not match '{}'. " \
                   .format(h1, h2)
    return msg


def check_row(row, value_checks):
    """
    :type row: list
    :param row: a list of values
    :type value_checks: list
    :param value_checks: a list of list, each nested list should consist
        of integer, function and a message string.
        The integer describes if the value in ``row`` is optional.
        The function is used to verify the value. If the function
        returns ``None``, the value had some problems and the message is
        used to describe the problem.
    :rtype: str
    :return: Error message if the given row does not match the criteria.
        If an empty string is returned, the ``row`` is ok.
    """
    msg = ""
    zipped = itertools.zip_longest(
        value_checks, row[:len(value_checks)], fillvalue=None)
    for i, ((required, check_func, temp_msg), value) in enumerate(zipped):
        # Skip optional columns
        if not required and value is None:
            continue
        if check_func(value) is None:
            msg += "Column {}, {}".format(i, temp_msg)
    return msg


def check_stf_file(filename):
    """
    Function to verify the '\*.stf' files. The format of such files is
    described in :ref:`STFFormat`.

    :type filename: str
    :param filename: path to '\*.stf' file to be checked
    """
    msg = ""
    linenbr = 0
    header_scope = False
    data_scope = False
    for row in fileutils.rowsof(filename, quiet=True):
        temp_msg = ""
        if row[0] == "HEADER":
            data_scope = False
            header_scope = True
        elif row[0] == "DATA":
            data_scope = True
            header_scope = False
        elif not any([linenbr, data_scope, header_scope]):
            temp_msg += "The file should start with 'HEADER' or 'DATA'. "
        elif header_scope:
            if len(row) != 2:
                temp_msg += "Incorrect length ({}), should be 2. " \
                    .format(len(row))
            else:
                key = row[0].split("_")[-1]
                if key not in outfilefields.STF_HEADER:
                    temp_msg += "Unidentified header field: {}. ".format(key)
                else:
                    _func, _msg = outfilefields.STF_HEADER[key]
                    if _func(row[1]) is None:
                        temp_msg += _msg
        elif data_scope:
            temp_msg += check_row(row, outfilefields.STF_DATA)
        if temp_msg:
            msg += "Line {}, {}\n".format(linenbr, temp_msg)
        linenbr += 1
    print_warning(filename, msg)


def check_csv_file(filename, value_checks=[], valid_header=[]):
    """
    Function to verify the '\*.alert' and '\*.csv' files.
    The format of such files is
    described in :ref:`AlertFormat` and :ref:`CSVFormat`.

    :type filename: str
    :param filename: path to a file to be checked
    :type value_checks: list, optional
    :param value_checks: a list passed to
        :func:`~polyfemos.scripts.check_output_files.check_row`
    :type valid_header: list, optional
    :param valid_header: a reference header used to verify the file header.
        See :func:`~polyfemos.scripts.check_output_files.check_header`
        for more info.
    """
    # The valid length for rows is solved by counting
    # the mandatory and optional columns
    maxlen = len(value_checks)
    minlen = sum(x[0] for x in value_checks)

    rows = fileutils.read_csv(filename, quiet=True)

    msg = ""
    for i, row in enumerate(rows):
        temp_msg = ""
        if i:
            if not minlen <= len(row) <= maxlen:
                temp_msg += "Incorrect length ({}), should be between " \
                            "{} and {}. ".format(len(row), minlen, maxlen)
            temp_msg += check_row(row, value_checks)
        else:
            # For the first row
            temp_msg += check_header(row, valid_header)
        if temp_msg:
            msg += "Line {}, {}\n".format(i, temp_msg)
    print_warning(filename, msg)


_check_funcs = {
    "stf": check_stf_file,
    "csv": functools.partial(check_csv_file,
                             value_checks=outfilefields.CSV_DATA,
                             valid_header=filewriter.get_csv_header("*")),
    "alert": functools.partial(check_csv_file,
                               value_checks=outfilefields.ALERT_DATA,
                               valid_header=filewriter.get_alert_header()),
}


def main(argv=None):
    """
    Recursively checks folders for polyfemos output
    files and check the validity of the files.
    If the exact file is given, only the given file is checked.

    If a single path to a directory is given, the directory is recursively
    checked for files with given extension.

    Wild cards in path can be used to give a list of paths.

    Printed row/line and column indices start at 0.

    :type argv: list
    :param argv: command line arguments
    """
    parser = ArgumentParser(prog='polyfemos-check',
                            description=__doc__.strip())
    parser.add_argument('extension', type=str, metavar='EXT',
                        help='The checked file extension, "stf", "csv", or '
                             '"alert"')
    parser.add_argument('paths', type=str, metavar='PATH', nargs='+',
                        help='Path to a file or folder, or list of paths.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print more than just warnings')

    args = parser.parse_args(argv)
    paths = args.paths
    verbose = args.verbose
    extension = args.extension

    if extension not in _check_funcs:
        print("The given extension is none of the following:")
        print("'stf', 'csv', or 'alert'")
        return

    if len(paths) == 1:
        path = paths[0]
        if os.path.isdir(path):
            paths = []
            for dirname, _, filenames in os.walk(path):
                for filename in filenames:
                    if filename.endswith(extension):
                        fn = os.path.join(dirname, filename)
                        paths.append(fn)

    some_checked = False
    for fn in paths:
        if fn.endswith(extension) and os.path.isfile(fn):
            if verbose:
                print("Checking file: {}".format(fn))
            _check_funcs[extension](fn)
            some_checked = True

    if not some_checked:
        print("No files checked, check paths: {}".format(paths))


if __name__ == "__main__":
    main()
