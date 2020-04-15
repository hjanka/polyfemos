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
Class :class:`~polyfemos.front.sohplot.sohplot.SOHPlot` for reading and
plotting state of health data

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import itertools

import numpy as np
from bokeh.embed import components
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import (DatetimeTickFormatter, HoverTool, FuncTickFormatter,
                          Range1d)

from polyfemos.parser import typeoperator as to
from polyfemos.util.messenger import messenger
from polyfemos.util import fileutils
from polyfemos.data import statistics
from polyfemos.almanac.utils import parse_date, get_jY
from polyfemos.front import (colors, userdef, request)
from polyfemos.front.sohplot import offsets, outfilefields
from polyfemos.front.sohplot.datacontainer import DataPoint, DataContainer


def _get_line_source(data, datarealtimeness=False):
    """
    :type data: list
    :param data: a list consisting of
        :class:`~polyfemos.front.sohplot.datacontainer.DataPoint` instances
    :type datarealtimeness: bool, optional
    :param datarealtimeness: If ``True``, datarealtimeness starttime value
        will be used to plot 'square' plots.
    :rtype: :class:`~bokeh.models.sources.ColumnDataSource`
    :return:
    """
    ys = []
    xs = []
    xs_str = []
    xs_str_ordinal = []

    def add_xy(dp):
        xs.append(dp.get_timezone_naive_datetime())
        xs_str.append(dp.get_dtstr())
        xs_str_ordinal.append(dp.get_ordinal())
        ys.append(dp.y)

    for i, dp in enumerate(data):
        # Only for plotting 'square' plot in the case of datarealtimeness
        # using z values starttimes
        if datarealtimeness:
            starttime = None
            dict_ = dp.get_z()
            if dict_ is not None:
                starttime = dict_.get('starttime', None)
            if starttime is not None and i > 0:
                dpm1 = data[i - 1]
                new_dp = DataPoint(dtstr=starttime, y=dp.y)
                if new_dp != dpm1:
                    add_xy(new_dp)
        add_xy(dp)

    line_source = ColumnDataSource(
        data={
            'xs': xs,  # python datetime object as X axis, local timezone
            'ys': ys,
            'xs_str': xs_str,  # string of datetime for displayed in tooltip
            'xs_str_ordinal': xs_str_ordinal,
        }
    )

    return line_source


def _plot_line_source(bokeh_figure, line_source, color="#000000", cross=False):
    """
    :type bokeh_figure: :class:`~bokeh.plotting.figure.Figure`
    :param bokeh_figure:
    :type line_source: :class:`~bokeh.models.sources.ColumnDataSource`
    :param line_source:
    :type color: str, optional
    :param color: color of the line or cross as string containing RGB value
        as hexadecimals (#RRBBGG), defaults to black
    :type cross: bool, optional
    :param cross: defaults to ``False``. If ``True``, crosses are plotted
        in any case. If ``False``, the cross marker is used for plotting
        If only 1 datapoint is present.
    """
    # If only one datapoint is present, use the cross marker
    if len(line_source.data['xs']) <= 1 or cross:
        line_ = bokeh_figure.cross(
            'xs',
            'ys',
            source=line_source,
            color=color,
            line_width=1,
            name='line',
            alpha=1,
            size=20,
        )
    else:
        line_ = bokeh_figure.line(
            'xs',
            'ys',
            source=line_source,
            color=color,
            line_width=1,
            name='line'
        )
    line_.visible = True


class SOHPlot(object):
    """
    Class for parsing and plotting the state of health data of given
    station and sohpar combination.

    Reads soh text files (the format is fixed).
    Plots the data from startdate to enddate.
    Creates statistical summary of the data.
    Removal of irrational values and advanced outlier removal possible.
    """
    def __init__(self, station_id="", sohpar_name="", startdate="",
                 enddate="", headerdate="", outlierremfunc=None,
                 remove_identicals=False,
                 remove_irrationals=False, advanced_outlier_removal=False,
                 fext="stf", track_datalen=False):
        """
        On initialization of SOHPlot, the data and header information are
        collected from the sohtextfiles. Optionally, irrational and
        outlying values are removed.

        ``startdate``, ``enddate`` and ``headerdate`` are parsed into
        python :class:`~datetime.date` instances using
        :func:`~polyfemos.almanac.utils.parse_date` function.

        :type station_id: str
        :param station_id: Station id in format ``NETWORK.STATION``,
            for example: ``FN.MSF``
        :type sohpar_name: str
        :param sohpar_name: State of health parameter available in sohtextfile.
        :type startdate: str
        :param startdate: The first date of the plotting timespan
        :type enddate: str
        :param enddate: The last date of the plotting timespan
        :type headerdate: str
        :param headerdate: The header information of this date's sohtextfile
            is used.
        :type outlierremfunc: func
        :param outlierremfunc: Defaults to ``None``. If no value is given,
            ``outlierremfunc`` for advanced outlier removal is retrieved
            using :func:`~polyfemos.front.userdef.summary_outlierremfuncs`.
            For more info see
            :meth:`~polyfemos.front.sohplot.datacontainer.DataContainer.outlier_removal`.
        :type remove_identicals: bool, optional
        :param remove_identicals: defaults to ``False``. If ``True``,
            values with identical x and y values are removed.
            see :class:`~polyfemos.front.sohplot.datacontainer.DataContainer`
            for more info
        :type remove_irrationals: bool, optional
        :param remove_irrationals: defaults to ``False``, see
            :meth:`~polyfemos.front.sohplot.datacontainer.DataContainer.remove_irrationals`
            for more info.
        :type advanced_outlier_removal: bool, optional
        :param advanced_outlier_removal: defaults to ``False``
        :type fext: str, optional
        :param fext: defaults to "stf", select "stf" or "csv",
            defines the datafile format which is read
        :type track_datalen: bool, optional
        :param track_datalen: Defaults to ``False``, If ``True``, the amount
            of datapoints, nans, etc., is monitored.
        """
        offsets.init_definitions()

        self.station_id = station_id
        self.sohpar_name = sohpar_name
        self.startdate = parse_date(startdate)
        self.enddate = parse_date(enddate)
        if self.startdate > self.enddate:
            self.startdate, self.enddate = self.enddate, self.startdate
        if not headerdate:
            self.headerdate = self.enddate
        else:
            self.headerdate = parse_date(headerdate)

        self.data_container = DataContainer(
            track_datalen=track_datalen,
            remove_identicals=remove_identicals
        )

        self.header = {}
        self.statistics_dict = None

        # If selected sohpar is N, E or Z offset and thus needs conversion
        nez = self.sohpar_name in offsets.NEZ_OFFSETS
        self._read_header(nez=nez)
        if nez or fext == "stf":
            self._read_stf_data(nez=nez)
        elif fext == "csv":
            self._read_csv_data()

        self.data_container.add_identical_removal_info()

        if remove_irrationals:
            irlims = self.header["IRLIMS"]
            self.data_container.remove_irrationals(irlims=irlims)

        if advanced_outlier_removal:
            if outlierremfunc is None:
                outlierremfunc = userdef.summary_outlierremfuncs(
                    station_id=self.station_id, sohpar_name=self.sohpar_name)
            self.data_container.outlier_removal(outlierremfunc=outlierremfunc)

    def get_info(self):
        """
        :rtype: list
        :return: A list containing info notes
        """
        return self.data_container.get_info()

    def get_statistics_dict(self):
        """
        :rtype: dict
        :return: see :func:`~polyfemos.data.statistics.get_statistics_dict`
            for more info
        """
        if self.statistics_dict is None:
            self.statistics_dict = statistics.get_statistics_dict(
                self.data_container.get_ys_wo_nans(),
                thresholds=self.header["YELLOW"],
                unit=self.header["UNIT"])
        return self.statistics_dict

    def get_statistics_table(self):
        """
        :rtype: list
        :return: see :func:`~polyfemos.data.statistics.get_statistics_table`
            for more info
        """
        return statistics.get_statistics_table(self.get_statistics_dict())

    def get_plot_components(self, decimate=True):
        """
        :type decimate: bool, optional
        :param decimate: defaults to ``True``,
            see :func:`~polyfemos.front.sohplot.sohplot.SOHPlot._get_plot`
        :rtype: str, str
        :return: script and div html blocks, see
            :func:`~bokeh.embed.components` for more information.
        """
        figure = self._get_plot(decimate=decimate)
        if figure is None:
            return "", ""
        return components(figure)

    def _get_filepath(self, date, fpf, extension, force=False):
        """
        :type date: :class:`~obspy.core.utcdatetime.UTCDateTime`
        :param date:
            is constructed from the ``root`` and ``fpf``, 'root/fpf(args)'
        :type fpf: func
        :param fpf: filepath format function
        :type extension: str
        :param extension: file extension
        :type force: bool
        :param force: see :func:`~polyfemos.front.request.filepath`
        :rtype: str
        :return: path to file
        """
        julday, year = get_jY(date)
        network_code, station_code = self.station_id.split(".")

        filepath = fpf(
            parname=self.sohpar_name,
            network_code=network_code,
            station_code=station_code,
            year=year,
            julday=julday)

        return request.filepath(filepath, extension, force=force)

    def _get_csv_filepath(self, date, extension=".csv", force=False):
        """
        :type date: :class:`~obspy.core.utcdatetime.UTCDateTime`
        :param date:
        :type force: bool
        :param force: see :func:`~polyfemos.front.request.filepath`
        :type extension: str
        :param extension: file extension, defaults to ``".csv"``
        :rtype: str
        :return: Filepath following the filepathformat defined in
            YAML config files.
        """
        return self._get_filepath(date, userdef.filepathformats("csv"),
                                  extension, force=force)

    def _get_stf_filepath(self, date):
        """
        :type date: :class:`~obspy.core.utcdatetime.UTCDateTime`
        :param date:
        :rtype: str
        :return: Filepath following the filepathformat defined in
            YAML config files.
        """
        return self._get_filepath(date, userdef.filepathformats("stf"), ".stf")

    def _read_header(self, nez=False):
        """
        Reads and parses the header information from the sohtextfile.
        Header block ends when 'DATA' text is encountered.

        :type nez: bool, optional
        :param nez: defaults to ``False``, for UWV to NEZ conversion,
            sensor information from the stf header is needed.
        """
        for key, values in outfilefields.STF_HEADER.items():
            # Fill the header with default values
            self.header[key] = values[-1]
        self.header["H_LINES"] = []

        rowstart = self.sohpar_name if self.sohpar_name else "_"
        if nez:
            rowstart = rowstart[:-1]

        filepath = self._get_stf_filepath(self.headerdate)
        if not filepath:
            msg = "Trying read the header of non existing 'stf' file."
            messenger(msg, "W")
            return
        for row in fileutils.rowsof(filepath):
            if len(row) >= 2:
                key = row[0]
                value = row[1]
                if key.startswith(rowstart):
                    key = key.split("_")[-1]
                if key in outfilefields.STF_HEADER:
                    self.header[key] = outfilefields.STF_HEADER[key][0](value)
            if row[0] == "DATA":
                break

        h_lines = self.header["YELLOW"] \
            + self.header["ORANGE"] + self.header["RED"]
        self.header["H_LINES"] = \
            [line for line in h_lines if not to.isNaN(line)]

    def _read_stf_data(self, nez=False):
        """
        Reads and parses the data from sohtextfiles.

        :type nez: bool, optional
        :param nez: defaults to ``False``. If selected sohpar is N, E or Z
            offset, values for U, W and V offsets has to be read.
            For information about UWV to NEZ conversion see
            :class:`~polyfemos.front.sohplot.offsets.UWVOffsets`
        """
        uwvo = offsets.UWVOffsets()
        stored_data = []

        runningdate = self.startdate
        while (runningdate <= self.enddate):
            filepath = self._get_stf_filepath(runningdate)
            data_scope = False
            runningdate += 86400
            if not filepath:
                continue
            for row in fileutils.rowsof(filepath):
                # Data values are read after 'DATA' text is encountered
                if row[0] == "DATA":
                    data_scope = True
                    continue
                if data_scope:
                    if len(row) < 3:
                        continue
                    stored_data.append(row)

        for row in stored_data:
            if nez and row[1] in uwvo.offsets:
                uwvo.update(*row[:3])
                # If U, W and V offset values are defined, conversion
                # can be done
                sensor = self.header["SENSOR"]
                if uwvo and sensor is not None:
                    dt, value = \
                        uwvo.transform(sensor, self.sohpar_name[-1])
                    uwvo.clear()
                else:
                    continue

            elif row[1] == self.sohpar_name:
                dt = to.utcdatetime(row[0])
                if dt is None:
                    msg = "Could not convert '{}' to utcdatetime." \
                        .format(row[0])
                    messenger(msg, "W")
                value = row[2]
            else:
                continue

            dp = DataPoint(utcdatetime=dt, y=value)

            if len(row) > 3:
                dp.set_z(row[3])

            self.data_container.append(dp)

    def _read_csv_data(self):
        """
        Reads the data from sohcsv files.
        """
        starttimestamp = self.startdate.timestamp
        endtimestamp = self.enddate.timestamp + 86399
        redd_filepaths = set()
        added_days = set()

        def read_file(fn, exclude_added_days=False):
            if not fn:
                return
            if fn in redd_filepaths:
                return
            redd_filepaths.add(fn)
            for row in fileutils.read_csv(fn)[1:]:
                if len(row) < 2:
                    continue
                dptimestamp = to.float_(row[0])
                if dptimestamp is None:
                    msg = ""
                    messenger(msg, "W")
                elif starttimestamp <= dptimestamp <= endtimestamp:
                    day = dptimestamp // 86400
                    if exclude_added_days and day in added_days:
                        continue
                    if not exclude_added_days:
                        added_days.add(day)
                    dp = DataPoint(timestamp=dptimestamp, y=row[1])
                    if len(row) > 2:
                        dp.set_z(row[2])
                    self.data_container.append(dp)

        runningdate = self.startdate
        while (runningdate <= self.enddate):

            filepath = self._get_csv_filepath(
                runningdate, force=True)
            retro_filepath = self._get_csv_filepath(
                runningdate, extension=".retro.csv", force=True)

            read_file(filepath)
            read_file(retro_filepath, exclude_added_days=True)

            runningdate += 86400

    def _get_plot(self, decimate=True):
        """
        Creates a 2D bokeh figure, time in x axis. By default, the data is
        plotted as a line, lines are separated if any number of nan values
        are between continuous set of valid values. If line consists of only
        one value, cross marker used instead of a line.
        Colors are as follows:

        - Red, actual data
        - Brighter red, horizontal lines defined by ``H_LINES``
        - Dark green, outlier datapoints

        :type decimate: bool, optional
        :param decimate: defaults to ``True``. If ``True``, data is decimated.
        :rtype: :class:`~bokeh.plotting.figure.Figure`
        :return:
        """
        BG_ALPHA = 1
        PLOT_W = 550
        PLOT_H = 480

        if len(self.data_container) < 1:
            return None

        if decimate:
            self.data_container.decimate()

        self.data_container.sort()

        dp0 = self.data_container.datapoints[0]
        dp1 = self.data_container.datapoints[-1]

        header = "{} {} {} - {}" \
            .format(self.station_id, self.sohpar_name,
                    dp0.get_ordinal(), dp1.get_ordinal())

        tools_to_use = \
            ['pan', 'box_zoom', 'wheel_zoom', 'hover', 'reset', 'save']

        bokehfig = figure(
            plot_width=PLOT_W,
            plot_height=PLOT_H,
            tools=tools_to_use,
            x_axis_type='datetime',
            title=header,
            output_backend="webgl",
        )

        bokehfig.border_fill_color = colors.GREY_1
        bokehfig.outline_line_color = colors.GREY_2
        bokehfig.background_fill_color = colors.GREY_3
        bokehfig.background_fill_alpha = BG_ALPHA

        tempunit = self.header["UNIT"]
        tempunit = "" if tempunit == "" else " ({})".format(tempunit)
        bokehfig.yaxis.axis_label = self.sohpar_name + tempunit
        bokehfig.xaxis.axis_label = "UTC Time"

        bokehfig.xaxis.axis_label_text_font = "Courier"
        bokehfig.yaxis.axis_label_text_font = "Courier"
        bokehfig.title.text_font = "Courier"
        bokehfig.xaxis.axis_label_text_font_style = "normal"
        bokehfig.yaxis.axis_label_text_font_style = "normal"
        bokehfig.title.text_font_style = "normal"
        bokehfig.xaxis.axis_label_text_color = colors.BLACK
        bokehfig.yaxis.axis_label_text_color = colors.BLACK
        bokehfig.title.text_color = colors.BLACK

        bokehfig.xaxis.axis_line_color = colors.BLACK
        bokehfig.yaxis.axis_line_color = colors.BLACK
        bokehfig.xaxis.major_label_text_color = colors.GREY_4
        bokehfig.yaxis.major_label_text_color = colors.GREY_4
        bokehfig.xaxis.minor_tick_line_color = colors.BLACK
        bokehfig.yaxis.minor_tick_line_color = colors.BLACK
        bokehfig.xaxis.major_tick_line_color = colors.BLACK
        bokehfig.yaxis.major_tick_line_color = colors.BLACK

        bokehfig.grid.grid_line_color = colors.GREY_2

        y_lim = self.header["PLOTLIMS"]
        if y_lim and len(y_lim) == 2:
            bokehfig.y_range = Range1d(*tuple(y_lim))

        bokehfig.yaxis.major_label_orientation = np.pi / 2
        ticklabelcode = userdef.ticklabels(self.sohpar_name)
        if ticklabelcode:
            bokehfig.yaxis.formatter = FuncTickFormatter(code=ticklabelcode)
            bokehfig.yaxis.major_label_orientation = np.pi * 7 / 16

        # Horisontal lines, multiline
        multiline_xs = []
        multiline_ys = []
        for y in self.header["H_LINES"]:
            multiline_xs.append([
                dp0.get_timezone_naive_datetime(),
                dp1.get_timezone_naive_datetime()
            ])
            multiline_ys.append([y, y])
        # Multiline data
        multiline_source = ColumnDataSource(
            data={
                'mlxs': multiline_xs,
                'mlys': multiline_ys,
            }
        )
        _ = bokehfig.multi_line(
            'mlxs',
            'mlys',
            source=multiline_source,
            color=colors.RED_1,
            line_width=1.5)

        datarealtimeness = \
            self.sohpar_name == userdef.definitions("datarealtimeness")

        all_data_split = [list(v) for k, v in itertools.groupby(
            self.data_container.datapoints, bool) if k]

        for md in all_data_split:
            main_line_source = \
                _get_line_source(md, datarealtimeness=datarealtimeness)
            _plot_line_source(bokehfig, main_line_source, color=colors.RED_3)

        if len(self.data_container.outlier_datapoints) > 0:
            outlier_data_split = [list(v) for k, v in itertools.groupby(
                self.data_container.outlier_datapoints, bool) if k]
            for od in outlier_data_split:
                outlier_line_source = \
                    _get_line_source(od, datarealtimeness=datarealtimeness)
                _plot_line_source(bokehfig, outlier_line_source,
                                  color=colors.GREEN, cross=True)

        hover = bokehfig.select(dict(type=HoverTool))

        hover.tooltips = [
            ("value", "@ys"),
            ("date", "@xs_str"),
            ("ordinal", "@xs_str_ordinal"),
        ]

        hover.mode = 'mouse'
        hover.names = ['line']

        bokehfig.xaxis.formatter = DatetimeTickFormatter(
            hours=["%d/%m/%Y %H:%M"],
            days=["%d/%m/%Y"],
            months=["%m/%Y"],
            years=["%Y"],
        )

        bokehfig.xaxis.major_label_orientation = np.pi / 5
        return bokehfig
