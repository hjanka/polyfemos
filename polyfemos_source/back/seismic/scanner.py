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
Scans available mseed files.

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
# I can hear myself... I think I'm a bit afraid
# They were drowning me
import glob
import itertools

import matplotlib.pyplot as plt
from obspy.imaging.scripts.scan import Scanner
from obspy import Trace, Stream

from polyfemos.almanac.ordinal import Ordinal
from polyfemos.front import colors


def data_coverage_image(flags, starttime, endtime, network_code, station_codes,
                        channel_codes, datafilepathfunc, outfilepathfunc):
    """
    Creates data coverage images using
    :class:`~obspy.imaging.scripts.scan.Scanner`.

    The available seismic data is scanned between times ``starttime``
    and ``endtime``. All channel and station combinations are included in the
    scan (``channel_codes`` and ``station_codes``).

    :type flags: dict
    :param flags: Flag variables from
        :class:`~polyfemos.back.interpreter.Interpreter`
    :type startime: :class:`~polyfemos.almanac.ordinal.Ordinal`
    :param startime:
    :type endtime: :class:`~polyfemos.almanac.ordinal.Ordinal`
    :param endtime:
    :type network_code: str
    :param network_code: Network code as a string, e.g. "FN"
    :type station_codes: list
    :param station_codes: list of string consisting of station codes,
        e.g. ``["MSF", "SGF", ...]``.
    :type channel_codes: list
    :param channel_codes: list of string consisting of channel codes,
        e.g. ``["HHZ", "HHE", ...]``.
    :type datafilepathfunc: func
    :param datafilepathfunc: A function returning filepaths to be included
        in the scan.
    :type outfilepathfunc: func
    :param outfilepathfunc: If the ``outfilepathfunc`` returns different
        filepaths with changing stations or channels etc., separate scanner
        plots are created with each different filepath.
    """
    # scanners dict stores 'outfilepath' and their corresponding scanner
    # instances
    scanners = {}
    pathkwargs = {}
    added_traces = set()

    _product = itertools.product(station_codes, channel_codes)
    for station_code, channel_code in _product:

        tr_id = "{}{}{}".format(network_code, station_code, channel_code)

        pathkwargs["network_code"] = network_code
        pathkwargs["station_code"] = station_code
        pathkwargs["channel_code"] = channel_code
        # Location in the seismic datafile paths is set to be anything
        pathkwargs["location_code"] = "*"

        for time_ in Ordinal.range(starttime, endtime):

            pathkwargs["year"] = time_.year
            pathkwargs["julday"] = time_.julday

            datafilepath = datafilepathfunc(**pathkwargs)
            outfilepath = outfilepathfunc(**pathkwargs)

            if outfilepath not in scanners:
                scanners[outfilepath] = Scanner()

            file_tr_key = outfilepath + tr_id
            # glob allows the usage of wildcards in the filepath
            for path in glob.glob(datafilepath):
                added_traces.add(file_tr_key)
                scanners[outfilepath].parse(path)

            if file_tr_key not in added_traces:
                tr = Trace()
                tr.stats.network = network_code
                tr.stats.station = station_code
                tr.stats.channel = channel_code
                tr_id = tr.get_id()
                st = Stream(traces=[tr])
                scanners[outfilepath].add_stream(st)
                added_traces.add(file_tr_key)

    for outfile, scanner in scanners.items():
        scanner.plot(outfile=outfile, starttime=starttime, endtime=endtime)


def null_figure(*args, **kwargs):
    """
    :rtype: :class:`~matplotlib.figure.Figure`
    :return: Empty figure
    """
    fig = plt.figure(figsize=(10, 1))
    plt.axis([-1, 1, -1, 1])
    text = "Nothing to show."
    plt.text(0, 0.5, text, fontsize=20, ha='center', va='top', wrap=True)
    plt.xticks([])
    plt.yticks([])
    plt.tight_layout()
    return fig


def get_data_coverage_figure(station_ids, channel_codes, startdate, enddate,
                             datafilepathfunc):
    """
    :type station_ids: list
    :param station_ids: station ids as a list of strings
    :type channel_codes: list
    :param channel_codes: data channel codes as a list of strings
    :type startdate: :class:`~obspy.core.utcdatetime.UTCDateTime`
    :param startdate: scanning startdate
    :type enddate: :class:`~obspy.core.utcdatetime.UTCDateTime`
    :param enddate: scanning enddate
    :type filepathfunc: func
    :param filepathfunc: A dynamic filepath, wildcards can be used since
        :func:`~glob.glob` is use to process filepaths after the
        arguments are filled in.
    :rtype: :class:`~matplotlib.figure.Figure`
    :return: scanner plot
    """
    scanner = Scanner()
    paths = []
    pathkwargs = {}
    pathkwargs["location_code"] = "*"
    network_and_station_codes = (s.split(".") for s in station_ids)
    combinations = \
        list(itertools.product(network_and_station_codes, channel_codes))
    date = startdate
    added_channels = set()
    while date <= enddate:
        pathkwargs["year"] = date.year
        pathkwargs["julday"] = date.julday
        for (network_code, station_code), channel_code in combinations:
            pathkwargs["network_code"] = network_code
            pathkwargs["station_code"] = station_code
            pathkwargs["channel_code"] = channel_code
            trace_key = network_code + station_code + channel_code
            paths = datafilepathfunc(**pathkwargs)
            for path in glob.glob(paths):
                scanner.parse(path)
                added_channels.add(trace_key)
        date += 86400

    count = len(added_channels)
    if count:
        height = 1.0 + count * 0.5
        height = min(height, 655.35)
        fig = scanner.plot(show=False, starttime=startdate, endtime=enddate)
        fig.set_size_inches(20.0, height)
        fig.set_facecolor(colors.WHITE)
        fig.tight_layout()
        return fig

    return null_figure()
