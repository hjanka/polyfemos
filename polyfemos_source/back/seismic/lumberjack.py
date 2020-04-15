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
Functions for reading and parsing data from state of health and data files.

The main public functions that return list of lists of timestamps and values:

- :func:`~polyfemos.back.seismic.lumberjack.data_mseed` (not yet)
- :func:`~polyfemos.back.seismic.lumberjack.centaur_mseed`
- :func:`~polyfemos.back.seismic.lumberjack.earthdata_mseed`
- :func:`~polyfemos.back.seismic.lumberjack.data_timing_quality_obspy_daily`
- :func:`~polyfemos.back.seismic.lumberjack.data_timing_quality`
- :func:`~polyfemos.back.seismic.lumberjack.data_coverage`

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
# I'm a lumberjack and I'm OK

import itertools
import functools

from obspy import Stream, UTCDateTime
from obspy.io.mseed.util import get_record_information, get_flags
from obspy.imaging.scripts.scan import Scanner

from polyfemos.parser import typeoperator as to
from polyfemos.util.messenger import messenger, debugger
from polyfemos.util import fileutils
from polyfemos.almanac.ordinal import Ordinal
from polyfemos.back import filewriter
from polyfemos.back.seismic import edlogreader


@fileutils.check_filepath
def data_mseed(path="", scale=lambda x: x, **kwargs):
    """
    TODO

    :type path:
    :param path:
    :type scale:
    :param scale:
    :rtype:
    :return:
    """
    # TODO paz correction
    # st = fileutils.get_stream(path)
    return None


@fileutils.check_filepath
@debugger
def get_earthdata_stream(path=""):
    """
    A function used with Earth Data state of health miniseed files.
    Parameter specific scaling function is applied to the raw data.

    :type path: str
    :param path: path to miniseed file
    :rtype: :class:`~obspy.core.stream.Stream` or None
    :return: seismic data stream
    """
    st = fileutils.get_stream(path=path)
    scale_funcs = {
        "AEP": lambda x: x,
        "AE1": lambda x: (x * 10.9 / 2700.0) + 5.0,  # to Volts
        "AE2": lambda x: x * 22.0 / 170.0,  # to Amperes
        "AE3": lambda x: (x / 10.0) - 50.0,  # to Degrees of Celcius
        "AE4": lambda x: (x * 10.9 / 2700.0) + 5.0,  # to Volts
        "AE5": lambda x: x / 1000.0,  # to Volts
        "AE6": lambda x: x / 1000.0,  # to Volts
        "AE7": lambda x: x / 1000.0,  # to Volts
        "AE8": lambda x: x / 1000.0,  # to Volts, Not in use
    }
    for tr in st:
        channel = tr.stats.channel
        if channel in scale_funcs:
            scale_func = scale_funcs[channel]
            tr.data = scale_func(tr.data)
    return st


@debugger
def stream_to_xy_data(st, scale=lambda x: x, **kwargs):
    """
    :type st: :class:`~obspy.core.stream.Stream`
    :param st: seismic data stream
    :type scale: func, optional
    :param scale: defaults to identity function,
        scaling function applied to data values
    :rtype: list or None
    :return: list of lists containing timestamp (as
        :class:`~obspy.core.utcdatetime.UTCDateTime` instance) and data value.
    """
    if len(st) < 1:
        return None
    tr_id = st[0].id
    st = st.select(id=tr_id)
    st.sort(keys=["starttime"])
    data = []
    for tr in st:
        starttime = tr.stats.starttime
        delta = tr.stats.delta
        data += [
            [starttime + i * delta, scale(dp)] for i, dp in enumerate(tr.data)
        ]
    return data


@fileutils.check_filepath
@debugger
def centaur_mseed(path="", scale=lambda x: x, **kwargs):
    """
    :type path: str
    :param path: path to miniseed file
    :type scale: func, optional
    :param scale: defaults to identity function,
        scaling function applied to data values
    :rtype: list or None
    :return: list of lists containing timestamp (as
        :class:`~obspy.core.utcdatetime.UTCDateTime` instance) and data value.
    """
    st = fileutils.get_stream(path)
    return stream_to_xy_data(st, scale=scale)


@fileutils.check_filepath
@debugger
def earthdata_mseed(path="", scale=lambda x: x, **kwargs):
    """
    :type path: str
    :param path: path to miniseed file
    :type scale: func, optional
    :param scale: defaults to identity function,
        scaling function applied to data values
    :rtype: list or None
    :return: list of lists containing timestamp (as
        :class:`~obspy.core.utcdatetime.UTCDateTime` instance) and data value.
    """
    st = get_earthdata_stream(path)
    return stream_to_xy_data(st, scale=scale)


@fileutils.check_filepath
@debugger
def data_timing_quality_obspy_daily(path="", key="", scale=lambda x: x,
                                    **kwargs):
    """
    Extract timing quality flags from given miniseed file. One value per
    file, which means one value per day.

    :type path: str
    :param path: path to miniseed file
    :type key: str
    :param key: key available with :func:`~obspy.io.mseed.util.get_flags` and
        ``timinig_quality`` key.
    :type scale: func, optional
    :param scale: defaults to identity function,
        scaling function applied to data values
    :rtype: list or None
    :return: list of lists containing timestamp (as
        :class:`~obspy.core.utcdatetime.UTCDateTime` instance) and data value.
    """
    dtq = get_flags(path)["timing_quality"]
    if key not in dtq:
        return None
    data_value = scale(dtq[key])
    st = fileutils.get_stream(path)
    st.sort(keys=["starttime"])
    time_ = st[-1].stats.endtime
    return [[time_, data_value]]


@fileutils.check_filepath
@debugger
def data_timing_quality(path="", average_calc_length=1, scale=lambda x: x,
                        **kwargs):
    """
    Reads timing quality values from miniseed file using
    :func:`~obspy.io.mseed.util.get_record_information` function.

    :type path: str
    :param path: path to miniseed file
    :type average_calc_length: int, optional
    :param average_calc_length: defaults to one, setting this value greater
        than one will result in a little bit smoothed timing quality curve,
        since the returned datapoints will be averages over
        ``average_calc_length`` values.
    :type scale: func, optional
    :param scale: defaults to identity function,
        scaling function applied to data values
    :rtype: list or None
    :return: list of lists containing timestamp (as
        :class:`~obspy.core.utcdatetime.UTCDateTime` instance) and data value.
    """
    imm = fileutils.invalid_mseed(path)
    if imm:
        messenger(imm, "M")
        return None

    timing_quality = []
    tqtimes = []
    last_qualities = []
    offset = 0

    # Codes from obspy
    # Loop over each record.
    # A valid record needs to have a record length of at
    # least 256 bytes.
    info = get_record_information(path)
    while offset <= (info['filesize'] - 256):
        this_info = get_record_information(path, offset)
        if 'timing_quality' in this_info:

            last_qualities.append(float(this_info['timing_quality']))
            length = len(last_qualities)
            ave = sum(last_qualities) / length
            if length > average_calc_length:
                last_qualities = last_qualities[1:]

            timing_quality.append(ave)
            tqtimes.append(this_info['starttime'])

        offset += this_info['record_length']

    return [[x, scale(y)] for x, y in zip(tqtimes, timing_quality)]


@debugger
def data_coverage(paths=[], starttime=None, endtime=None, scale=lambda x: x,
                  invalid_value=0.0):
    """
    Calculates the datacoverage percentage between ``starttime`` and
    ``endtime``.

    See :class:`~obspy.imaging.scripts.scan.Scanner` and
    :meth:`~obspy.imaging.scripts.scan.Scanner.analyze_parsed_data`
    for more information.

    :type paths: list
    :param paths: list of filepaths (as string values)
        to the datefiles to be scanned
    :type starttime: :class:`~obspy.core.utcdatetime.UTCDateTime`
    :param starttime:
    :type endtime: :class:`~obspy.core.utcdatetime.UTCDateTime`
    :param endtime:
    :type scale: func, optional
    :param scale: defaults to identity function,
        scaling function applied to data values
    :type invalid_value: float, optional
    :param invalid_value: default to ``0.0``
    :rtype: list or None
    :return: list of lists containing timestamp (as
        :class:`~obspy.core.utcdatetime.UTCDateTime` instance), data value,
        and additional z value as string.
    """
    if starttime is None or endtime is None:
        return None

    if starttime > endtime:
        starttime, endtime = endtime, starttime

    st0 = Stream()
    for path in paths:
        st = fileutils.get_stream(path)
        if st is None:
            continue
        st0 += st

    percentage = invalid_value
    # Arbitrary z_value as string following python dictionary syntax
    z_value = "{{'starttime':'{}'}}".format(str(starttime))

    if len(st0) > 0:
        scanner = Scanner()
        scanner.add_stream(st0)
        scanner.analyze_parsed_data(starttime=starttime, endtime=endtime)
        percentage = scanner._info[st0[0].id]['percentage']
        percentage = invalid_value if percentage is None else percentage
        percentage = scale(percentage)

    return [[endtime, percentage, z_value]]


###
# Privates start here
###


def _none2invalid(generator):
    """
    Decorates private lumberjack functions.
    Replaces ``None`` values with function specific invalid values.
    The default invalid value is defined in function
    :func:`~polyfemos.parser.typeoperator.getNaN`.

    :type generator: :obj:`~types.GeneratorType`
    :param generator:
    :rtype: :obj:`~types.GeneratorType`
    :return: decorated generator
    """
    @functools.wraps(generator)
    def wrapper(*args, **kwargs):
        if "invalid_value" not in kwargs:
            kwargs["invalid_value"] = to.getNaN()
        for time_, data in generator(*args, **kwargs):
            if data is None:
                data = [
                    [time_, kwargs['invalid_value']]
                ]
            yield time_, data
    return wrapper


@_none2invalid
def _data_mseed(pathfunc, times, flags, funckwargs={}, **kwargs):
    """
    TODO

    See the documentation of
    :func:`~polyfemos.back.seismic.lumberjack._data_coverage`.

    :type pathfunc:
    :param pathfunc:
    :type times:
    :param times:
    :type flags:
    :param flags:
    :type funckwargs:
    :param funckwargs:
    :rtype:
    :return:
    """
    data_mseed
    yield None


@_none2invalid
def _centaur_mseed(pathfunc, times, flags, funckwargs={}, **kwargs):
    """
    Generator calling function
    :func:`~polyfemos.back.seismic.lumberjack.centaur_mseed`
    [\*] see the documentation of
    :func:`~polyfemos.back.seismic.lumberjack._data_coverage`.

    :type pathfunc: func
    :param pathfunc: [\*]
    :type times: list
    :param times: [\*]
    :type flags: dict
    :param flags: [\*]
    :type funckwargs: dict, optional
    :param funckwargs: defaults to empty dict, keyword arguments for
        :func:`~polyfemos.back.seismic.lumberjack.centaur_mseed`
    :return: generator yielding :class:`~obspy.core.utcdatetime.UTCDateTime`
        and list of lists of timestamps and data values
    """
    for time_ in times:
        path = pathfunc(julday=time_.julday, year=time_.year)
        yield time_, centaur_mseed(path=path, **funckwargs)


@_none2invalid
def _earthdata_mseed(pathfunc, times, flags, funckwargs={}, **kwargs):
    """
    Generator calling function
    :func:`~polyfemos.back.seismic.lumberjack.earthdata_mseed`
    [\*] see the documentation of
    :func:`~polyfemos.back.seismic.lumberjack._data_coverage`.

    :type pathfunc: func
    :param pathfunc: [\*]
    :type times: list
    :param times: [\*]
    :type flags: dict
    :param flags: [\*]
    :type funckwargs: dict, optional
    :param funckwargs: defaults to empty dict, keyword arguments for
        :func:`~polyfemos.back.seismic.lumberjack.earthdata_mseed`
    :return: generator yielding :class:`~obspy.core.utcdatetime.UTCDateTime`
        and list of lists of timestamps and data values
    """
    for time_ in times:
        path = pathfunc(julday=time_.julday, year=time_.year)
        yield time_, earthdata_mseed(path=path, **funckwargs)


@_none2invalid
def _data_timing_quality(pathfunc, times, flags, funckwargs={}, **kwargs):
    """
    Generator calling function
    :func:`~polyfemos.back.seismic.lumberjack.data_timing_quality`
    [\*] see the documentation of
    :func:`~polyfemos.back.seismic.lumberjack._data_coverage`.

    :type pathfunc: func
    :param pathfunc: [\*]
    :type times: list
    :param times: [\*]
    :type flags: dict
    :param flags: [\*], adds ``average_calc_lengthy`` flag to ``funckwargs``
    :type funckwargs: dict, optional
    :param funckwargs: defaults to empty dict, keyword arguments for
        :func:`~polyfemos.back.seismic.lumberjack.data_timing_quality`
    :return: generator yielding :class:`~obspy.core.utcdatetime.UTCDateTime`
        and list of lists of timestamps and data values
    """
    funckwargs["average_calc_length"] = flags["average_calc_length"]
    for time_ in times:
        path = pathfunc(julday=time_.julday, year=time_.year)
        yield time_, data_timing_quality(path=path, **funckwargs)


@_none2invalid
def _data_timing_quality_obspy_daily(pathfunc, times, flags, funckwargs={},
                                     key="", **kwargs):
    """
    Generator calling function
    :func:`~polyfemos.back.seismic.lumberjack.data_timing_quality_obspy_daily`
    [\*] see the documentation of
    :func:`~polyfemos.back.seismic.lumberjack._data_coverage`.

    :type pathfunc: func
    :param pathfunc: [\*]
    :type times: list
    :param times: [\*]
    :type flags: dict
    :param flags: [\*]
    :type funckwargs: dict, optional
    :param funckwargs: defaults to empty dict, keyword arguments for
        :func:`~polyfemos.back.seismic.lumberjack.data_timing_quality_obspy_daily`
    :type key: str
    :param key: Adds the ``key`` to ``funckwargs``,
        see :func:`~obspy.io.mseed.util.get_flags` ``timing_quality``
        for available keys
    :return: generator yielding :class:`~obspy.core.utcdatetime.UTCDateTime`
        and list of lists of timestamps and data values
    """
    funckwargs["key"] = key
    for time_ in times:
        path = pathfunc(julday=time_.julday, year=time_.year)
        yield time_, data_timing_quality_obspy_daily(path=path, **funckwargs)


@_none2invalid
def _earthdata_log(pathfunc, times, flags, funckwargs={}, key="", **kwargs):
    """
    Generator calling function
    :func:`~polyfemos.back.seismic.edlogreader.get_data`
    [\*] see the documentation of
    :func:`~polyfemos.back.seismic.lumberjack._data_coverage`.

    :type pathfunc: func
    :param pathfunc: [\*]
    :type times: list
    :param times: [\*]
    :type flags: dict
    :param flags: [\*]
    :type funckwargs: dict, optional
    :param funckwargs: defaults to empty dict, keyword arguments for
        :func:`~polyfemos.back.seismic.edlogreader.get_data`
    :type key: str
    :param key: Adds the ``key`` to ``funckwargs``,
        see :mod:`~polyfemos.back.seismic.edlogreader` for available keys
    :return: generator yielding :class:`~obspy.core.utcdatetime.UTCDateTime`
        and list of lists of timestamps and data values
    """
    funckwargs["key"] = key
    for time_ in times:
        path = pathfunc(julday=time_.julday, year=time_.year)
        datapoint = edlogreader.get_data(path=path, **funckwargs)
        # If datapoint is None, yield single None as data so the _none2invalid
        # decorator works
        if datapoint is not None:
            datapoint = [[time_, datapoint]]
        yield time_, datapoint


@_none2invalid
@debugger
def _data_coverage(pathfunc, times, flags, funckwargs={},
                   key="DCL", invalid_value=0.0):
    """
    The documentation of this function will cover all of the
    next private generator functions of lumberjack:

    - :func:`~polyfemos.back.seismic.lumberjack._data_mseed`
    - :func:`~polyfemos.back.seismic.lumberjack._centaur_mseed`
    - :func:`~polyfemos.back.seismic.lumberjack._earthdata_mseed`
    - :func:`~polyfemos.back.seismic.lumberjack._earthdata_log`
    - :func:`~polyfemos.back.seismic.lumberjack._data_timing_quality`
    - :func:`~polyfemos.back.seismic.lumberjack._data_timing_quality_obspy_daily`
    - :func:`~polyfemos.back.seismic.lumberjack._data_coverage`
    - :func:`~polyfemos.back.seismic.lumberjack._data_timestamp_error`

    All of these generator functions are decorated with
    :func:`~polyfemos.back.seismic.lumberjack._none2invalid`
    which means that all ``None``
    data values are replaced with ``invalid_value``

    :type pathfunc: func
    :param pathfunc: A function taking julian date and year as keyword
        arguments and returning path as a string
    :type times: list
    :param times: a list of :class:`~obspy.core.utcdatetime.UTCDateTime`
        instances
    :type flags: dict
    :param flags: Flag variables from
        :class:`~polyfemos.back.interpreter.Interpreter`
    :type funckwargs: dict, optional
    :param funckwargs: defaults to empty dict, keyword arguments for
        :func:`~polyfemos.back.seismic.lumberjack.data_coverage`
    :type key: str, optional
    :param key: "DCD" (for data coverage from the startof the day) or "DCL"
        (for the data coverage from the start program start, i.e.
        realtimeness)
    :type invalid_value: float, optional
    :param invalid_value: defaults to ``0.0``, i.e. no data available
    :return: generator yielding :class:`~obspy.core.utcdatetime.UTCDateTime`
        and list of lists of timestamps and data values, in this case, the
        data contains only one value.
    """
    realtimeness_limit = flags["realtimeness_limit"]
    pklfile = flags["execution_time_file"]
    timedict = fileutils.load_obj(pklfile)
    dc_starttime = timedict["laststarttime"] - realtimeness_limit
    dc_endtime = timedict["thisstarttime"] - realtimeness_limit
    if key == "DCD":
        dc_starttime = UTCDateTime(dc_endtime.strftime("%Y%j"))
    paths = []
    lasttimes = times[:][-1:]
    for time_ in [lasttimes[0] - 86400, lasttimes[0]]:
        paths.append(pathfunc(julday=time_.julday, year=time_.year))

    funckwargs["paths"] = paths
    funckwargs["starttime"] = dc_starttime
    funckwargs["endtime"] = dc_endtime
    funckwargs["invalid_value"] = invalid_value

    yield lasttimes[0], data_coverage(**funckwargs)


@_none2invalid
def _data_timestamp_error(pathfunc, times, flags, funckwargs={}, **kwargs):
    """
    Calculates the time difference (in seconds) between current program
    starttime and timestamp of the last datapoint in the data file. The
    difference is positive if datapoint's timestamp is lesser of the two.

    [\*] see the documentation of
    :func:`~polyfemos.back.seismic.lumberjack._data_coverage`.

    :type pathfunc: func
    :param pathfunc: [\*]
    :type times: list
    :param times: [\*]
    :type flags: dict
    :param flags: [\*]
    :type funckwargs: dict, optional
    :param funckwargs: defaults to empty dict,
    """
    time_ = times[:][-1]
    path = pathfunc(julday=time_.julday, year=time_.year)
    st = fileutils.get_stream(path)
    if st is None or len(st) < 1:
        yield time_, None
    else:
        pklfile = flags["execution_time_file"]
        timedict = fileutils.load_obj(pklfile)
        programstarttime = timedict["thisstarttime"]
        endtime = sorted([tr.stats.endtime.timestamp for tr in st])[-1]
        datapoint = programstarttime.timestamp - endtime
        if 'scale' in funckwargs:
            datapoint = funckwargs['scale'](datapoint)
        yield programstarttime, [[programstarttime, datapoint]]


@debugger
def _get_data(station, par, times, flags):
    """
    Format of the values yielded by the returned generator

    .. code-block:: text

        (day1,
            [
                [timestamp11, value11],
                [timestamp12, value12],
                ...
            ],
        ),
        (day2,
            [
                [timestamp21, value21],
                [timestamp22, value22],
                ...
            ],
        ),
        ...

    :type station: :class:`~polyfemos.back.station.Station`
    :param station: station object containing
    :type par: :class:`~polyfemos.back.parameter.Parameter`
    :param par:
    :type times: list
    :param times: a list of :class:`~obspy.core.utcdatetime.UTCDateTime`
        instances
    :type flags: dict
    :param flags: Flag variables from
        :class:`~polyfemos.back.interpreter.Interpreter`
    :rtype: generator
    :return: A generator yielding timestamp for each day and the data of that
        day, (timestamps and datapoints) for that day.
    """
    if len(times) < 1:
        return None
    pathkwargs = {}
    pathkwargs["network_code"] = station.network_code
    pathkwargs["station_code"] = station.station_code
    pathkwargs["location_code"] = station.location_code
    pathkwargs["channel_code"] = par.channel_code
    pathkwargs["parname"] = par.name
    pathfunc = functools.partial(par.path, **pathkwargs)

    funckwargs = {}
    funckwargs["scale"] = par.scale
    data_generator = _functions[par.code](
        pathfunc, times, flags,
        funckwargs=funckwargs)
    return data_generator


_functions = {
    # Nanometrics Centaur state of health parameters available from MSEED
    "EX1": _centaur_mseed,  # External SOH channels, 1-3
    "EX2": _centaur_mseed,
    "EX3": _centaur_mseed,
    "LCE": _centaur_mseed,  # Absolute clock phase error
    "LCQ": _centaur_mseed,  # Clock quality
    "VCO": _centaur_mseed,  # Timing oscillator control voltage
    "VEC": _centaur_mseed,  # Digitizer system current
    "VM1": _centaur_mseed,  # Sensor SOH channels, Offset voltages, 1-6
    "VM2": _centaur_mseed,
    "VM3": _centaur_mseed,
    "VM4": _centaur_mseed,
    "VM5": _centaur_mseed,
    "VM6": _centaur_mseed,
    "VPB": _centaur_mseed,  # Digitizer buffer percent used
    "GNS": _centaur_mseed,  # Number of GPS satellites used
    "GLA": _centaur_mseed,  # GPS latitude
    "GLO": _centaur_mseed,  # GPS longitude
    "GEL": _centaur_mseed,  # GPS elevation
    "GST": _centaur_mseed,  # GPS status
    "GPL": _centaur_mseed,  # GPS PPL status
    "VDT": _centaur_mseed,  # Digitizer system temperature
    "VEI": _centaur_mseed,  # Input system voltage
    "GAN": _centaur_mseed,  # GPS antenna status
    # Earth Data LOG parameters
    # 16 bit phase error in 1 second pll
    "LOG.plle": functools.partial(_earthdata_log, key="plle"),
    # Date as six integer sequence
    "LOG.date": functools.partial(_earthdata_log, key="date"),
    # Time as six integer sequence
    "LOG.time": functools.partial(_earthdata_log, key="time"),
    # Latitude in WGS84 system
    "LOG.lat": functools.partial(_earthdata_log, key="lat",
                                 invalid_value=-1),
    # Longitude in WGS84 system
    "LOG.long": functools.partial(_earthdata_log, key="long",
                                  invalid_value=-1),
    # Heading
    "LOG.hdng": functools.partial(_earthdata_log, key="hdng"),
    # Velocity
    "LOG.vel": functools.partial(_earthdata_log, key="vel"),
    # Magnetic variation
    "LOG.mva": functools.partial(_earthdata_log, key="mva"),
    # Earth Data state of health parameters available from MSEED
    "AEP": _earthdata_mseed,  # 16 bit phase error in 1 second pll
    "AE1": _earthdata_mseed,  # Supply voltage at supply connector/input
    "AE2": _earthdata_mseed,  # Supply current
    "AE3": _earthdata_mseed,  # Temp. sensor voltage, internal temperature
    "AE4": _earthdata_mseed,  # Supply voltage at remote connector/input
    "AE5": _earthdata_mseed,  # User input  Offset
    "AE6": _earthdata_mseed,  # -//-        Offset
    "AE7": _earthdata_mseed,  # -//-        Offset
    "AE8": _earthdata_mseed,  # Not in use
}
_data_functions = [
    # Other parameters available from raw data MSEEDs
    ["", _data_mseed],  # Data files
    [".TQ", _data_timing_quality],  # Timing quality
    # Data Coverage Day, Percentage of coverage from start of the day
    [".DCD", functools.partial(_data_coverage, key="DCD", invalid_value=0.0)],
    # Data Coverage Last, Percentage of coverage since last check
    [".DCL", functools.partial(_data_coverage, key="DCL", invalid_value=0.0)],
    # Timing quality minimum, Reads timing_quality parameters
    # from mseed header blockette 1001
    [".TQMIN", functools.partial(_data_timing_quality_obspy_daily, key="min")],
    # Timing quality maximum
    [".TQMAX", functools.partial(_data_timing_quality_obspy_daily, key="max")],
    # Timing quality average
    [".TQAVE", functools.partial(_data_timing_quality_obspy_daily,
                                 key="mean")],
    [".TQMED", functools.partial(_data_timing_quality_obspy_daily,
                                 key="median")],  # Timing quality median
    # Timing quality lower quartile
    [".TQLOQ", functools.partial(_data_timing_quality_obspy_daily,
                                 key="lower_quartile")],
    # timimg quality upper quartile
    [".TQUPQ", functools.partial(_data_timing_quality_obspy_daily,
                                 key="upper_quartile")],
    [".TSE", _data_timestamp_error],  # data timestamp error
]
# Create all possible data channels "HHZ", "HHE", etc...
_data_channels = ("".join(c) for c in itertools.product("HBLV", "H", "ZNE"))
# Combine all possible data channels with possible functions used with
# the channels
for dc, df in itertools.product(_data_channels, _data_functions):
    _functions[dc + df[0]] = df[1]
# Functions consists of all the functions that can be called using the
# code of the parameter
# The first characters of the code (before dot if present)
# are the CHANNEL of the parameter in mseed     or in other files.
# What comes after the dot is internally called 'code_key'.


@debugger
def get_tibs(alertfunc, data):
    """
    The ``alertfunc`` is applied to the ``data``, starting from the first
    value of the ``data`` iterable.

    :type alertfunc: func
    :param alertfunc: A function taking (usually) a numerical value as
        an argument and returning a boolean value. Returned value is ``True``
        if the 'threshold is broken'.
    :type data: iterable
    :param data: An iterable containing the data values
    :rtype: bool, bool
    :return: The ``tib`` is ``True`` if the first value of the ``data``
        breaks the threshold, ``thbb`` is ``True`` if any value of the
        ``data`` breaks the threshold. NaN value may be returned if
        all data points are NaNs or the alerts are not valid.
    """
    tib, thbb = to.getNaN(), False
    i = 0
    for dp in data:
        if dp is None:
            continue
        if to.isNaN(dp):
            continue
        alert = bool(alertfunc(dp))
        if alert is None:
            continue
        # tib = True, only if the first value breaks the threshold
        tib = i == 0 and alert
        # thbb = True, if any data point breaks the threshold
        # The iteration is immediately terminated
        thbb |= alert
        if thbb:
            break
        i += 1
    thbb = tib if to.isNaN(tib) else thbb
    return tib, thbb


@debugger
def _get_tibs_dc(alertfunc, data, alertfile, parname=""):
    r"""
    Since :func:`~_data_coverage` function return only one data point
    each time it is called. The 'threshold has been broken' (``thbb``)
    value is not meaningfull. This function is used to read earlier ``tib``
    and ``thbb`` values adn to set the ``thbb`` value accordingly.

    :type alertfunc: func
    :param alertfunc: see
        :func:`~polyfemos.back.seismic.lumberjack.get_tibs` for more info
    :type data: iterable
    :param data: An iterable containing the data values
    :type alertfile: str
    :param alertfile: A path to '\*.alert' file, the
        'threshold has been broken' value is read from the file if it exists.
    :type parname: str
    :param parname: the name of the parameter with a code 'DCD' or 'DCL'.
        The ``thbb`` value is searched from the ``alertfile`` using the
        ``parname``.
    :rtype: bool, bool
    :return: see
        :func:`~polyfemos.back.seismic.lumberjack.get_tibs` for more info
    """
    tib, thbb = get_tibs(alertfunc, data)
    rows = fileutils.read_csv(alertfile)
    if to.isNaN(tib) or tib or rows is None:
        return tib, thbb
    for row in rows:
        if len(row) < 3:
            continue
        if row[1] == parname:
            thbb |= row[2] in "12"
            break
    return tib, thbb


@debugger
def _get_tibs(par, data, alertfile):
    """
    :type par: :class:`~polyfemos.back.parameter.Parameter`
    :param par:
    :type data: list
    :param data: A list of lists of timestamps and data values
    :type alertfile: str
    :param alertfile: see
        :func:`~polyfemos.back.seismic.lumberjack._get_tibs_dc` for more info
    :rtype: bool, bool
    :return: see :func:`~polyfemos.back.seismic.lumberjack.get_tibs`
        for more info
    """
    # create generator yielding only the y values of the data
    # starting from the last entry
    data_gen = (dp[1] for dp in reversed(data))
    if par.code_key in {"DCD", "DCL"}:
        return _get_tibs_dc(par.alertfunc, data_gen, alertfile,
                            parname=par.name)
    else:
        return get_tibs(par.alertfunc, data_gen)


def _station_and_times(stations, network_code, station_code,
                       starttime, endtime):
    """
    A function used to select right
    :class:`~polyfemos.back.station.Station` instances
    for time within timeinterval from ``starttime`` to ``endtime``.

    The names of the network_code and station will be same for all
    :class:`~polyfemos.back.station.Station`
    instances returned, but other values
    and parameters of the station may change during the timespan.
    At the moment, only day accuracy is supported when selecting right
    stations.

    :type stations: :class:`~polyfemos.back.station.Stations`
    :param stations:
    :type network_code: str
    :param network_code: Network code as a string, e.g. "FN"
    :type station_code: str
    :param station_code: Code of the station as a string, e.g. "MSF"
    :type starttime: :class:`~polyfemos.almanac.ordinal.Ordinal`
    :param starttime:
    :type endtime: :class:`~polyfemos.almanac.ordinal.Ordinal`
    :param endtime:
    :return: generator yielding
        :class:`~polyfemos.back.station.Station` instances and
        list of times when the station is valid.
    """
    stations_dict = {}
    times_dict = {}
    for time_ in Ordinal.range(starttime, endtime):
        station = stations.get_station(network_code, station_code, time_)
        key = "{}{}".format(id(station), time_.year)
        if key not in stations_dict:
            stations_dict[key] = station
            times_dict[key] = [time_.utcdatetime()]
        else:
            times_dict[key].append(time_.utcdatetime())

    for key, station in stations_dict.items():
        yield station, times_dict[key]


def process_logs(flags, stations, network_code, station_code,
                 starttime, endtime, classes):
    r"""
    Gathers data from various sources, parses the data and
    writes '\*.stf', '\*.alert' and '\*.csv' files.

    Processes data for stations with given
    ``network_code`` and ``station_code``.

    :type flags: dict
    :param flags: Flag variables from
        :class:`~polyfemos.back.interpreter.Interpreter`
    :type stations: :class:`~polyfemos.back.station.Stations`
    :param stations: The station information collected from '\*.conf' files.
    :type network_code: str
    :param network_code: Network name as a string, e.g. "FN"
    :type station_code: str
    :param station_code: Name of the station as a string, e.g. "MSF"
    :type startime: :class:`~polyfemos.almanac.ordinal.Ordinal`
    :param startime:
    :type endtime: :class:`~polyfemos.almanac.ordinal.Ordinal`
    :param endtime:
    :type classes: list
    :param classes: list of strings containing all parameter classes
        which are included in the station's state of health processing.
    """
    retroactive = flags["retroactive"]

    alert_writer = filewriter.AlertWriter(
        bool_=flags["write_sohalertfile"],
        fp_func=flags['sohalertpath'],
        retroactive=retroactive,
    )
    csv_writer = filewriter.CSVWriter(
        bool_=flags["write_sohcsvfile"],
        fp_func=flags['sohcsvpath'],
        retroactive=retroactive,
    )
    stf_writer = filewriter.STFWriter(
        bool_=flags["write_sohtextfile"],
        fp_func=flags['sohtextfilepath'],
        retroactive=retroactive,
    )

    last_year = None

    sxt = _station_and_times(
        stations, network_code, station_code, starttime, endtime)
    for station, times in sxt:

        this_year = times[0].year
        if last_year is None:
            last_year = this_year
        if retroactive and this_year != last_year:
            csv_writer.write_files()
            last_year = this_year

        pathkwargs = {}
        pathkwargs["network_code"] = station.network_code
        pathkwargs["station_code"] = station.station_code

        station.filter_parameters(class_=classes)
        stf_writer.update_header(station.get_header())

        for par in station.parameters:

            pathkwargs["parname"] = par.name

            csv_writer.update_header(filewriter.get_csv_header(par.unit))

            # DCD, DCL and TSE parameters cannot be used retroactively
            if retroactive and par.code_key in {"DCD", "DCL", "TSE"}:
                continue

            for time_, data in _get_data(station, par, times, flags):

                if data is None:
                    continue

                if len(data) < 1:
                    continue

                pathkwargs["julday"] = time_.julday
                pathkwargs["year"] = time_.year

                # alert
                alertfilename = alert_writer.get_filename(pathkwargs)
                tib, thbb = _get_tibs(par, data, alertfilename)
                alertline = [station.id,
                             par.name,
                             tib + thbb,
                             par.priority,
                             data[-1][0].timestamp]
                alert_writer.append_line(alertfilename, alertline)

                csvfilename = csv_writer.get_filename(pathkwargs)
                stffilename = stf_writer.get_filename(pathkwargs)

                if not retroactive:
                    lastvalues = data[-1]
                    csv_writer.append_and_write_data(csvfilename, lastvalues)
                    stf_writer.append_and_write_data(stffilename, lastvalues,
                                                     par.name)

                if retroactive:
                    for datavalues in data[::par.decimation_factor]:
                        csv_writer.append_data(csvfilename, datavalues)
                        stf_writer.append_data(stffilename, datavalues,
                                               par.name)

        alert_writer.write_files()

        if retroactive:
            stf_writer.write_files()

    if retroactive:
        csv_writer.write_files()
