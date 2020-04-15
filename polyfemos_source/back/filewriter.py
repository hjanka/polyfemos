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
Contains classes for writing state of health files

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import functools

from polyfemos.util import fileutils


def get_csv_header(unit, *args):
    """
    :type unit: str
    :param unit: unit of the parameter values
    :rtype: list
    :return: soh csv file header as list of strings
    """
    return ["utctimestamp", "value [{}]".format(unit), "z"]


def get_alert_header(*args):
    """
    :rtype: list
    :return: soh alert file header as list of strings
    """
    return ["station_id", "parameter", "alert", "priority", "last_dp_ts"]


def create_stfline(values, parname, *args):
    r"""
    :type values: list
    :param values: 2-3 value list, [timevalue, y, z]
    :type parname: str
    :param parname: parameter name
    :rtype: str
    :return: line for '\*.stf' file following the soh text file format
    """
    stfline = values[:]
    stfline.insert(1, parname)
    str_ = "".join("{:30}".format(str(r)) for r in stfline).strip()
    str_ += "\n"
    return str_


def create_csvline(values, *args):
    r"""
    :type values: list
    :param values: 2-3 value list, [timevalue, y, z]
    :rtype: list
    :return: row for '\*.csv' file, the timevalue is replaced with
        the corresponding timestamp
    """
    return [values[0].timestamp] + values[1:]


def _check_bool(method):
    """
    A decorator to be used with :class:`~polyfemos.back.filewriter.FileWriter`.
    The call of the decorated method is omitted if ``self._bool``
    attribute is ``False``.

    :type method: func
    :param method: A decorated method
    :rtype: func
    :return:
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self._bool:
            return method(self, *args, **kwargs)
        return None
    return wrapper


class FileWriter(object):
    """
    Parent class for state of health file writer classes
    """
    def __init__(self, bool_=False, fp_func=None, retroactive=False):
        """
        The attribute values are suitable for writing state of health
        csv files by default.

        ``self._file_writing_func`` is set to
        :func:`~polyfemos.util.fileutils.write_csv`.

        ``self._create_line_func`` is set to
        :func:`~polyfemos.back.filewriter.create_csvline`.

        :type bool\_: bool
        :param bool\_: If ``False``, methods of this class do nothing,
            If ``fp_func`` is not callable, ``bool_`` is set to ``False``
        :type fp_func: func
        :param fp_func: filepath function, e.g. FLAGs 'sohtextfilepath'
            'sohalertpath' or 'sohcsvpath'. See
            :meth:`~polyfemos.back.interpreter.Interpreter._init_flags`
            for more information.
        :type retroactive: bool
        :param retroactive: defines if the retroactive mode is used.
            See :meth:`~polyfemos.back.interpreter.Interpreter._init_flags`
            for more info.
        """
        bool_ &= callable(fp_func)
        self._bool = bool_
        self._filepath_func = fp_func
        self._retroactive = retroactive

        self._dict = {}
        self._header = None
        self._suffix = "csv"
        self._file_writing_func = fileutils.write_csv
        self._create_line_func = create_csvline

    @_check_bool
    def get_filename(self, pathkwargs):
        """
        Applies ``pathkwargs`` to ``self._filepath_func`` and returns
        the resulting filepath. If retroactive mode is used, 'retro'
        identifier is added to the filepath.

        :type pathkwargs: dict
        :param pathkwargs: keyword arguments for ``self._filepath_func``
        :rtype: str
        :return:
        """
        retro = ".retro" if self._retroactive else ""
        fn = self._filepath_func(**pathkwargs)
        fn += "{}.{}".format(retro, self._suffix)
        return fn

    @_check_bool
    def update_header(self, header):
        """
        :type header: str or list
        :param header: a new header applied to ``self._header``
        """
        self._header = header

    @_check_bool
    def append_line(self, filename, line):
        """
        If there is no file with a name ``filename`` in ``self._dict``,
        header is added to the corersponding file entry in ``self._dict``.

        :type filename: str
        :param filename:
        :type line: list
        :param line: A line to be appended into the file (``filename``)
            entry in ``self._dict``.
        """
        if filename not in self._dict:
            self._dict[filename] = [self._header]
        self._dict[filename].append(line)

    @_check_bool
    def append_data(self, filename, *args):
        """
        Additional arguments ``args`` are applied to the
        function ``self._create_line_func``.

        Creates and appends a new line to file entry (``filename``)
        in ``self._dict``.

        :type filename: str
        :param filename:
        """
        line = self._create_line_func(*args)
        self.append_line(filename, line)

    @_check_bool
    def append_and_write_data(self, filename, *args):
        """
        Additional arguments ``args`` are applied to the
        function ``self._create_line_func``.

        Creates and immediately writes a new line to file ``filename``.

        :type filename: str
        :param filename:
        """
        line = self._create_line_func(*args)
        fileutils.append_to_file(filename, line, self._header)

    @_check_bool
    def write_files(self):
        """
        Writes out every file in ``self._dict`` and deletes the data
        contained in it.
        """
        for filename, rows in self._dict.items():
            self._file_writing_func(filename, rows)
        self._dict = {}


class CSVWriter(FileWriter):
    r"""
    State of health csv file ('\*.csv') writer
    """
    def __init__(self, *args, **kwargs):
        """
        See :meth:`~polyfemos.back.filewriter.FileWriter.__init__`
        for more info.
        """
        super().__init__(*args, **kwargs)


class AlertWriter(FileWriter):
    r"""
    State of health alert file ('\*.alert') writer
    """
    def __init__(self, *args, **kwargs):
        """
        ``self._header`` is set to a fixed value returned by
        :func:`~polyfemos.back.filewriter.get_alert_header`.

        See :meth:`~polyfemos.back.filewriter.FileWriter.__init__`
        for more info.
        """
        super().__init__(*args, **kwargs)
        self._header = get_alert_header()
        self._suffix = "alert"


class STFWriter(FileWriter):
    r"""
    State of health text file ('\*.stf') writer
    """
    def __init__(self, *args, **kwargs):
        """
        ``self._file_writing_func`` is set to
        :func:`~polyfemos.util.fileutils.write_file`.

        ``self._create_line_func`` is set to
        :func:`~polyfemos.back.filewriter.create_stfline`.

        See :meth:`~polyfemos.back.filewriter.FileWriter.__init__`
        for more info.
        """
        super().__init__(*args, **kwargs)
        self._file_writing_func = fileutils.write_file
        self._create_line_func = create_stfline
        self._suffix = "stf"

    @_check_bool
    def append_line(self, filename, line):
        """
        If there is no file with a name ``filename`` in ``self._dict``,
        header is added to the corersponding file entry in ``self._dict``.

        :type filename: str
        :param filename:
        :type line: str
        :param line: Line to be appended into the file (``filename``)
            entry in ``self._dict``.
        """
        if filename not in self._dict:
            self._dict[filename] = self._header
        self._dict[filename] += line
