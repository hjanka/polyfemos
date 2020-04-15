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
Web forms

Forms use :class:`~flask_wtf.FlaskForm` as a base form

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
from obspy import UTCDateTime

import flask_wtf
from wtforms.fields import (DateField, BooleanField,
                            FloatField, RadioField, SelectField,
                            IntegerField, SubmitField, SelectMultipleField)

from polyfemos.front import userdef


class SubmitForm(flask_wtf.FlaskForm):
    """
    A web form for submit button.
    """
    submit = SubmitField(u'Submit')


class SingleDateForm(flask_wtf.FlaskForm):
    """
    A web form for submitting a single date.
    """
    date = DateField(u'Date', default=UTCDateTime().now().date,
                     format='%Y-%m-%d')


class DateForm(flask_wtf.FlaskForm):
    """
    A web form for submitting start and end dates.
    """
    startdate = DateField(u'Startdate', default=UTCDateTime().now().date,
                          format='%Y-%m-%d')
    enddate = DateField(u'Enddate', default=UTCDateTime().now().date,
                        format='%Y-%m-%d')


class StationsForm(flask_wtf.FlaskForm):
    """
    A web form for submitting a station selection as a string
    """
    _choices = [(s, s) for s in userdef.station_ids()]
    station_ids = SelectMultipleField(u'Stations', choices=_choices)


class SelectNetworkForm(flask_wtf.FlaskForm):
    """
    A web form to select network
    """
    _choices = [(s, s) for s in userdef.network_codes()]
    network_code = SelectField(u'Select Network', choices=_choices)


class DatacoverageForm(SubmitForm, DateForm, StationsForm):
    """
    A web form for :func:`~polyfemos.front.main.datacoveragebrowser`.
    """
    _choices = [(s, s) for s in userdef.channel_codes()]
    channel_codes = SelectMultipleField(u'Channels', choices=_choices)


class HeaderdateForm(flask_wtf.FlaskForm):
    """
    A web form for submitting a single date
    """
    headerdate = DateField(u'Headerdate', default=UTCDateTime().now().date,
                           format='%Y-%m-%d')


class RIRVForm(flask_wtf.FlaskForm):
    """
    A web form for 'Remove irrational values' check box
    """
    rirv = BooleanField(u'Remove irrational values', default="")


class FileFormatForm(flask_wtf.FlaskForm):
    """
    Web form for selecting input fileformat
    """
    _choices = [(s, s) for s in ["csv", "stf"]]
    fromfileformat = SelectField(u'Read from', choices=_choices)


class SummaryForm(SubmitForm, DateForm, HeaderdateForm, RIRVForm,
                  FileFormatForm, StationsForm):
    """
    A web form for :func:`~polyfemos.front.main.summary`.
    """
    aor = BooleanField(u'Advanced outlier removal', default="")
    csv_requested = BooleanField(u'Download csv', default="")

    _choices = [(s, s) for s in userdef.sohpars(visibilities={1, 2, 3})]
    sohpar_names = SelectMultipleField(u'Sohpars', choices=_choices)


class PlotbrowserForm(SubmitForm, StationsForm, DateForm, FileFormatForm,
                      HeaderdateForm, RIRVForm):
    """
    A web form for :func:`~polyfemos.front.main.plotbrowser`.
    """
    _choices = [(s, s) for s in userdef.sohpars(visibilities={1, 2, 3})]
    sohpar_names = SelectMultipleField(u'Sohpars', choices=_choices)

    decimate = BooleanField(u'Decimate', default="checked")
    ridv = BooleanField(u'Remove identical values', default="checked")
    track_len = BooleanField(u'Track data length', default="checked")

    aor = RadioField(u'Advanced outlier removal', choices=[
        ('null', 'None'),
        ('dtr', 'DTR'),
        ('sta', 'STALTA'),
        ('lip', 'Lipschitz'),
    ])

    dtr_maxdepth = IntegerField(u'maxdepth', default=0)
    dtr_scale = FloatField(u'scale', default=24000)
    dtr_medlim = FloatField(u'medlim', default=10)

    sta_nsta = IntegerField(u'nsta', default=3)
    sta_nlta = IntegerField(u'nlta', default=10)
    sta_threson = FloatField(u'threson', default=1.08)
    sta_thresoff = FloatField(u'thresoff', default=1.05)
    sta_offset = IntegerField(u'offset', default=40)

    lip_itern = IntegerField(u'itern', default=1)
    lip_klim = FloatField(u'klim', default=7e-5)


class SohTableForm(SubmitForm, SingleDateForm):
    """
    A web form for :func:`~polyfemos.front.main.sohtable`.
    """
    show_all = BooleanField(u'Show all', default="checked")
    submit_pd = SubmitField(u'+date')
    submit_sd = SubmitField(u'-date')
    realtimeness_limit = IntegerField(u'Realtimeness limit', default=120)
    realtimeness_bool = BooleanField(u'Realtimeness filter',
                                     default="checked")


class AlertHeatForm(SubmitForm, DateForm):
    """
    A web form for :func:`~polyfemos.front.main.alertheat`.
    """
    log_color = BooleanField(u'Logarithmic color', default="")

    _choices = [(int(s), s) for s in "012"]
    points_per_thbb = SelectField(u'Points per thbb', choices=_choices,
                                  default=1, coerce=int)
    points_per_tib = SelectField(u'Points per tib', choices=_choices,
                                 default=2, coerce=int)
