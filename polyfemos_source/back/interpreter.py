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
Contains :class:`~polyfemos.back.interpreter.Interpreter` for reading
'\*conf' files

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import os
import copy
import functools

import pathos.multiprocessing as mp
from obspy import UTCDateTime

from polyfemos.parser import typeoperator as to
from polyfemos.util.messenger import messenger, debugger
from polyfemos.util import fileutils
from polyfemos.parser import resources
from polyfemos.back.seismic import lumberjack, scanner
from polyfemos.back.parameter import Parameter
from polyfemos.back.station import Station, Stations


def pool_error_callback(arg, msg=""):
    """
    A function to be called during pool worker error

    :type arg:
    :param arg: Error message
    :type msg: str, optional
    :param msg: Additional message
    """
    msg += "while using multiprocessing\n"
    msg += str(arg) + "\n"
    messenger(msg, "E", showpid=False)


def check_quit(func_):
    """
    A decorator to be used with methods of class
    :class:`~polyfemos.back.interpreter.Interpreter`. If the class
    attribute ``self._quit`` is set to ``False``, the decorated methods
    do nothing.

    :type func\_: func
    :param func\_:
    :rtype: func
    :return:
    """
    @functools.wraps(func_)
    def wrapper(self, *args, **kwargs):
        if not self._quit:
            return func_(self, *args, **kwargs)
    return wrapper


class Interpreter(object):
    r"""
    Class for reading '\*.conf' files

    Contents of the '\*.conf' files are
    interpreted at run time.
    """
    def __init__(self):
        """
        Sets the global program starttime, ``self.__now``.
        Calls :meth:`~polyfemos.back.interpreter.Interpreter._init_timedict`
        to initialize ``self.__timedict``.

        Creates empty :class:`~polyfemos.back.station.Stations()` instance
        (``self.station``).
        """
        self._quit = False
        self.__now = UTCDateTime(precision=0)

        self.stations = Stations()
        self.vars = {}
        self.scopes = {"station": False}
        self.__rlm = ""  # reader location message
        self.__current_conf_folder = ""
        self._init_flags()

        self.pool = None

        self._init_timedict()

        self._init_funcs_and_commands(self.__now)

        messenger("", "B")
        messenger("Program starttime: " + str(self.__now), "R")

    def _init_timedict(self):
        """
        Sets 'thisstarttime' and 'laststarttime' values to
        ``self.__now``.
        """
        self.__timedict = {
            "thisstarttime": self.__now,
            "laststarttime": self.__now,
        }

    def _init_flags(self):
        r"""
        Ititializes ``self.__flags`` and ``self.flags`` dictionaries.
        ``self.__flags`` consists of flag types and default values.
        ``self.flags`` will store the flag values, changed or default.

        If default value of the FLAG is ``None``, the user most likely needs
        to provide correct value in the '\*.conf' file.

        All available FLAGs, their types and default values:

        .. rubric:: sohtextfilepath

        :func:`~polyfemos.parser.typeoperator.filepath`, ``None``,
        Filepath of the output '\*.stf' file. Do not include
        file extension when defining the path, the corresponding
        extension will be automatically included.


        .. rubric:: sohalertpath

        :func:`~polyfemos.parser.typeoperator.filepath`, ``None``,
        Filepath of the output '\*.alert' file. Do not include
        file extension when defining the path, the corresponding
        extension will be automatically included.


        .. rubric:: sohcsvpath

        :func:`~polyfemos.parser.typeoperator.filepath`, ``None``,
        Filepath of the output '\*.csv' file. Do not include
        file extension when defining the path, the corresponding
        extension will be automatically included.


        .. rubric:: wait_after_midnight

        :func:`~polyfemos.parser.typeoperator.int_`, ``0``,
        Given in seconds. As the START command is called, if difference
        between current program starttime and midnight is lesser
        than this value, program execution is halted
        (without saving any starttime values).


        .. rubric:: write_sohalertfile

        [not in use]

        :func:`~polyfemos.parser.typeoperator.bool_`, ``True``,
        Defines if '\*.alert' file is created/updated


        .. rubric:: write_sohtextfile

        [not in use]

        :func:`~polyfemos.parser.typeoperator.bool_`, ``True``,
        Defines if '\*.stf' file is created/updated


        .. rubric:: write_sohcsvfile

        [not in use]

        :func:`~polyfemos.parser.typeoperator.bool_`, ``True``,
        Defines if '\*.csv' file is created/updated


        .. rubric:: retroactive

        :func:`~polyfemos.parser.typeoperator.bool_`, ``False``

        If ``False``, appends lines to previously created files.
        One new line per station-parameter combination.

        If ``True``, creates '\*.stf' and '\*.csv' files from scratch,
        Files created retroactively, have an additional 'retro'
        identifier in the filename. Retroactive option
        overwrites previously created 'retro'-files.


        .. rubric:: save_starttime

        :func:`~polyfemos.parser.typeoperator.bool_`, ``False``,
        Defines if current program starttime is saved to 'laststarttime'
        when program execution is finished


        .. rubric:: realtimeness_limit

        :func:`~polyfemos.parser.typeoperator.int_`, ``0``,
        Given in seconds, for datacoverage parameters (codes 'DCD' and
        'DCL'), defines the time interval in which the data is still
        considered to be in "realtime". See
        :func:`~polyfemos.back.seismic.lumberjack._data_coverage`
        for more info.


        .. rubric:: average_calc_length

        :func:`~polyfemos.parser.typeoperator.int_`, ``1``,
        Sets the ``average_calc_length`` in
        :func:`~polyfemos.back.seismic.lumberjack.data_timing_quality`,
        which is used for codes 'XXX.TQ'.


        .. rubric:: execution_time_file

        :func:`~polyfemos.parser.typeoperator.staticfilepath`, ``None``,
        A pickle file where 'thisstarttime' and 'laststarttime' program
        starttime values are saved and available for reference via
        this FLAG during program execution. Include the full path in the
        definition including the extension (\*.pkl).


        .. rubric:: multiprocessing

        :func:`~polyfemos.parser.typeoperator.bool_`, ``True``,
        Defines if multiprocessing is used or not.


        .. rubric:: max_processes

        :func:`~polyfemos.parser.typeoperator.int_`, ``4``,
        Maximum number of CPUs used for multiprocessing,
        see :meth:`~polyfemos.back.interpreter.Interpreter._init_pool` for
        more info.
        """
        self.flags = {}
        self.__flags = {}

        self.__flags["sohtextfilepath"] = \
            {'type': to.filepath, 'value': None}
        self.__flags["sohalertpath"] = {'type': to.filepath, 'value': None}
        self.__flags["sohcsvpath"] = {'type': to.filepath, 'value': None}

        self.__flags["wait_after_midnight"] = {'type': to.int_, 'value': 0}
        self.__flags["write_sohalertfile"] = {'type': to.bool_, 'value': True}
        self.__flags["write_sohtextfile"] = {'type': to.bool_, 'value': True}
        self.__flags["write_sohcsvfile"] = {'type': to.bool_, 'value': True}
        self.__flags["retroactive"] = {'type': to.bool_, 'value': False}
        self.__flags["save_starttime"] = {'type': to.bool_, 'value': False}
        self.__flags["realtimeness_limit"] = {'type': to.int_, 'value': 0}
        self.__flags["average_calc_length"] = {'type': to.int_, 'value': 1}

        self.__flags["execution_time_file"] = \
            {'type': to.staticfilepath, 'value': None}
        self.__flags["multiprocessing"] = {'type': to.bool_, 'value': True}
        self.__flags["max_processes"] = {'type': to.int_, 'value': 4}

        # copy values from self.__flags to self.flags
        for k, v in self.__flags.items():
            self.flags[k] = v['value']

    def _init_pool(self):
        """
        Initializes ``self.pool``
        (:class:`~pathos.multiprocessing.ProcessPool`)
        attribute. Sets the maximum amount of CPUs used by the pool,
        this is defined with the FLAG `max_processes`.
        Two CPUs are left unused if possible (i.e. the machine has 3 or more
        CPUs). In every case the pool will use at least 1 CPU.
        See :meth:`~polyfemos.back.interpreter.Interpreter.apply_async`
        for more info.

        If ``self.pool`` is already initialized, do nothing.
        """
        if self.pool is not None:
            return
        maxprocs = mp.cpu_count() - 2
        maxprocs = max(1, maxprocs)
        maxprocs = min(self.flags["max_processes"], maxprocs)
        maxprocs = max(1, maxprocs)
        self.pool = mp.Pool(processes=maxprocs, maxtasksperchild=1)

    def replace_var(self, key):
        """
        :type key: str
        :param key: the name of the variable starting with the variable symbol
        :rtype: str
        :return: Anything contained in ``self.vars[key]``, if ``key`` is
            previously defined variable.
        """
        if not key.startswith(resources.SYMBOLS["VAR"]):
            return key
        if key in self.vars:
            return self.vars[key]
        return None

    def save_starttime(self, tolast=False):
        """
        If ``tolast`` is ``False``, loads the 'laststarttime' value from the
        pklfile (FLAG `execution_time_file`) before saving the
        ``self.__timedict``. After this the 'laststarttime' should be
        unchanged, and 'thisstarttime' should contain the starttime of this
        exact program run.

        If ``tolast`` is ``True``, the value of 'thisstarttime' is saved
        to 'laststarttime'.

        :type tolast: bool, optional
        :param tolast: defaults to ``False``
        """
        pklfile = self.flags['execution_time_file']
        msg = self.__rlm
        if pklfile is None:
            msg += "FLAG \'execution_time_file\' undefined"
            messenger(msg, "E")
            return
        if not os.path.isdir(os.path.dirname(pklfile)):
            msg += "FLAG \'execution_time_file\' {}\n".format(pklfile)
            msg += "Directory does not exist"
            messenger(msg, "E")
            return
        if not os.path.isfile(pklfile) or tolast:
            self._init_timedict()
            fileutils.save_obj(pklfile, self.__timedict)
            return
        loaded_dict = fileutils.load_obj(pklfile)
        if "laststarttime" in loaded_dict:
            self.__timedict["laststarttime"] = loaded_dict["laststarttime"]
        fileutils.save_obj(pklfile, self.__timedict)

    def apply_async(self, func_, args, deepcopy=True):
        r"""
        Asynchronously calls ``func_`` with ``args`` using
        :class:`~pathos.multiprocessing.ProcessPool` (alias of
        ``multiprocess.pool.Pool`` from
        `multiprocess <https://pypi.org/project/multiprocess/>`_). Additional
        information in Python's own multiprocessing package
        :obj:`~multiprocessing.pool.Pool`.

        If ``deepcopy`` and
        ``self.flags["multiprocessing"]`` are both ``False``, the function is
        called normally ``func_(*args)``.

        :type func\_: func
        :param func\_:
        :type args: list
        :param args: arguments to the ``func_``
        :type deepcopy: bool, optional
        :param deepcopy: defaults to ``True``, only used if multiprocessing
            is not used. If ``True``, the ``args`` are deepcopied before
            calling the ``func_``.
        """
        if self.flags["multiprocessing"]:
            self._init_pool()
            _ecb = functools.partial(pool_error_callback, msg=self.__rlm)
            self.pool.apply_async(func_, args=args, error_callback=_ecb)
        else:
            if deepcopy:
                args = copy.deepcopy(args)
            func_(*args)

    def close_and_join(self):
        """
        If ``self.pool`` is previously set up, terminates the pool workers by
        calling methods close and join.
        """
        if self.pool is None:
            return
        self.pool.close()
        self.pool.join()

    ###
    # Functions available using commands
    ###

    @debugger
    @check_quit
    def readfile(self, conffile):
        r"""
        Reads and interprets contents of the '\*.conf' files.

        :type conffile: str
        :param conffile: path to '\*.conf' file
        """
        conffile = os.path.join(self.__current_conf_folder, conffile)
        msg = "Reading conffile: {}".format(conffile)
        messenger(msg, "R")

        if not os.path.isfile(conffile):
            msg = "Given conffile ({}) does not exist".format(conffile)
            messenger(msg, "E")
            return

        self.__current_conf_folder = os.path.dirname(conffile)
        rows = fileutils.read_file(conffile)

        linenbr = 0
        for row in rows:
            linenbr += 1
            # remove linebreaks and whitespaces at start and end of the row
            row = row.strip()
            # If row does not start with \ skip the row
            if not row or row[0] != resources.SYMBOLS["CMD"]:
                continue
            # save file and line information for debugging
            self.__rlm = "File \"{}\", line {}\n".format(conffile, linenbr)
            self.__rlm += "  {}\n".format(row)
            # Remove everything from the row after #-symbol
            if resources.SYMBOLS["COMMENT"] in row:
                row = row[:row.index(resources.SYMBOLS["COMMENT"])]
            # Split the row according the whitespaces
            # and remove extra whitespaces
            row = [r for r in row.split() if r]

            command = row[0]
            args = row[1:]

            # Check if given command is defined
            if command not in self.commands:
                msg = self.__rlm
                msg += "Unidentified command \'{}\'".format(command)
                messenger(msg, "E")
                continue

            # Check if any station definition is before parameter definition
            if command == resources.CMDS["PAR"] and not self.scopes["station"]:
                msg = self.__rlm
                msg += "Trying to add parameter before station."
                messenger(msg, "E")
                return

            # extract list of functions to be applied to arguments
            argtypes = self.commands[command]['argtypes'][:]

            # If RUN command is used
            # Check if called function exists and modify argument types
            # accordingly
            if command == resources.CMDS["RUN"]:
                msg = self.__rlm
                msg += "Using command \'{}\', ".format(resources.CMDS["RUN"])
                if len(argtypes) <= 0:
                    msg += "no function name given"
                    messenger(msg, "E")
                    return
                elif not args[0] in self.functions:
                    msg += "no function \'{}\' available".format(args[0])
                    messenger(msg, "E")
                    return
                argtypes += self.functions[args[0]]['argtypes']

            # Check if correct amount of arguments is given, raise error if not
            if len(args) != len(argtypes):
                msg = self.__rlm
                msg += "Invalid amount of arguments with given " \
                    "command \'{}\'\n".format(command)
                if command == resources.CMDS["RUN"]:
                    msg += "with function \'{}\'\n".format(args[0])
                msg += "Arguments given {}, should be {}" \
                    .format(len(args), len(argtypes))
                messenger(msg, "E")
                return

            newargs = [self.replace_var(arg) for arg in args]
            for i, arg in enumerate(newargs):
                if arg is None:
                    msg = self.__rlm
                    msg += "Variable \'{}\' at index {} is not defined." \
                        .format(args[i], i)
                    messenger(msg, "E")
                    return

            # Convert arguments into their rightful types
            # raise error if conversion is not possible
            newargs = [f(arg) for f, arg in zip(argtypes, newargs)]
            for i, arg in enumerate(newargs):
                if arg is None:
                    msg = self.__rlm
                    msg += "Argument with invalid type or syntax\n"
                    msg += "Given \'{}\' at index {}, should be of type {}" \
                        .format(args[i], i, argtypes[i].__name__)
                    messenger(msg, "E")
                    return

            self.commands[command]['func'](*newargs)

    @debugger
    @check_quit
    def define_flag(self, flag, value):
        """
        :type flag: str
        :param flag: name of the FLAG
        :type value:
        :param value: value of the FLAG, the type depends on the flag
        """
        if flag not in self.__flags:
            msg = self.__rlm
            msg += "No FLAG \'{}\' available.".format(flag)
            messenger(msg, "E")
            return
        self.flags[flag] = self.__flags[flag]["type"](value)

    @debugger
    @check_quit
    def define_var(self, key, value):
        """
        :type key: str
        :param key: variable name
        :type value: str
        :param value: value to be set to variable
        """
        self.vars[key] = value

    @debugger
    @check_quit
    def add_station(self, *args):
        """
        Tries to define and add a station
        (:class:`~polyfemos.back.station.Station`)
        instance to ``self.stations``. ``args`` are passed straight to the
        :meth:`~polyfemos.back.station.Station.__init__`.
        """
        station = Station(*args)
        success = self.stations.add_station(station)
        if not success:
            msg = self.__rlm
            msg += "Unable to add station with id {}\n".format(station.id)
            msg += "Start or endtimes overlap"
            messenger(msg, "E")
            return
        self.scopes["station"] = True

    @debugger
    @check_quit
    def add_par(self, *args):
        """
        Creates :class:`~polyfemos.back.parameter.Parameter`
        instance and adds it to the most recently defined station in
        ``self.stations``. ``args`` are passed straight to the
        :meth:`~polyfemos.back.parameter.Parameter.__init__`.
        """
        self.stations.add_parameter(Parameter(*args))

    @debugger
    @check_quit
    def exit_scope(self):
        """
        Effectively does nothing at the moment
        """
        self.scopes["station"] = False

    @debugger
    @check_quit
    def call_func(self, funckey, *args):
        """
        Calls function available in ``self.functions``.

        ``args`` are the
        arguments passed to the function ``self.functions[funckey]['func']``.

        :type funckey: str
        :param funckey: name of the function
        """
        self.functions[funckey]['func'](*args)

    @check_quit
    def start(self):
        """
        Program execution is halted if the difference between program
        starttime and midnight is lesser than value of the FLAG
        'wait_after_midnight'.

        Saves the current program starttime to 'thisstarttime'.
        see :meth:`~polyfemos.back.interpreter.Interpreter.save_starttime`
        for more info.
        """
        midnight = UTCDateTime(self.__now.strftime("%Y%j"))
        if self.__now - midnight < self.flags["wait_after_midnight"]:
            self.stop(save_starttime=False)
        else:
            self.save_starttime()

    @check_quit
    def stop(self, quit_=True, save_starttime=True):
        """
        :type quit\_: bool, optional
        :param quit\_: defaults to ``True``, If ``True`` the program does
            nothing anymore.
        :type save_starttime: bool, optional
        :param save_starttime: defaults to ``True``, In order to save
            starttime value, ``save_starttime`` and FLAG 'save_starttime'
            both are required to be ``True``.
        """
        for k, v in self.__timedict.items():
            msg = "{}: {}".format(k, v)
            messenger(msg, "N")
        self.close_and_join()
        if save_starttime and self.flags["save_starttime"]:
            self.save_starttime(tolast=True)
        if quit_:
            self._quit = True

    ###
    # Functions available using RUN command
    ###

    @debugger
    def data_coverage_image(self, *args):
        """
        Calls :func:`~polyfemos.back.seismic.scanner.data_coverage_image`
        with ``self.flags`` and ``args``.
        """
        self.apply_async(scanner.data_coverage_image, (self.flags, *args))

    @debugger
    def plot_ppsd(self, *args):
        """
        TODO

        ``args``
        """
        pass

    @debugger
    def process_logs(self, *args):
        """
        Processes all stations in ``self.stations``.
        Calls :func:`~polyfemos.back.seismic.lumberjack.process_logs`
        with ``self.flags``, ``self.stations``, and ``args``.
        """
        self.apply_async(lumberjack.process_logs,
                         (self.flags, self.stations, *args))

    def _init_funcs_and_commands(self, today):
        """
        All possible commands in addition to functions called using the
        'RUN' command are defined here. Additionally, the amount of arguments
        and their types for each function and command is defined.

        If today special variable is used in case of types
        :func:`~polyfemos.parser.typeoperator.ordinal` or
        :func:`~polyfemos.parser.typeoperator.utcdatetime`,
        the variable is replaced with
        the value of ``today``.

        :type today: :class:`~obspy.core.utcdatetime.UTCDateTime`
        :param today:
        """
        # set TODAY special variable correctly when type is
        # ordinal or utcdatime
        _ordinal = functools.partial(to.ordinal, today=today)
        _utcdatetime = functools.partial(to.utcdatetime, today=today)
        # Functions available using RUN command
        self.functions = {
            "process_logs": {
                'func': self.process_logs,
                'argtypes': [
                    to.str_, to.str_, _ordinal, _ordinal, to.strlist]},
            "data_coverage_image": {
                'func': self.data_coverage_image,
                'argtypes': [
                    _utcdatetime, _utcdatetime, to.str_, to.strlist,
                    to.strlist, to.filepath, to.filepath]},
        }
        # Commads available
        self.commands = {
            resources.CMDS["IMPORT"]: {
                'func': self.readfile,
                'argtypes': [to.str_]},
            resources.CMDS["FLAG"]: {
                'func': self.define_flag,
                'argtypes': [to.str_, to.str_]},
            resources.CMDS["VAR"]: {
                'func': self.define_var,
                'argtypes': [to.var, to.str_]},
            resources.CMDS["END"]: {
                'func': self.exit_scope,
                'argtypes': []},
            resources.CMDS["START"]: {
                'func': self.start,
                'argtypes': []},
            resources.CMDS["STOP"]: {
                'func': self.stop,
                'argtypes': []},
            resources.CMDS["RUN"]: {
                'func': self.call_func,
                'argtypes': [to.str_]},
            resources.CMDS["STATION"]: {
                'func': self.add_station,
                'argtypes': [
                    to.str_, to.str_, to.str_, to.float_, to.float_,
                    to.str_, to.str_, to.str_, _ordinal, _ordinal]},
            resources.CMDS["PAR"]: {
                'func': self.add_par,
                'argtypes': [
                    to.str_, to.str_, to.str_, to.int_, to.float_,
                    to.str_, to.floatlist, to.int_, to.function, to.floatlist,
                    to.floatlist, to.filepath]},
        }
