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
A script for sending state of health alerts via email

The script may be run for example using cron to check and notify about
the active alerts daily. See more information in :ref:`SOHEmailer`.

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import os
import itertools
import email
import smtplib

from argparse import ArgumentParser

from polyfemos.parser import typeoperator as to
from polyfemos.util import fileutils
from polyfemos.front.alertreader import get_sohdict
from polyfemos.almanac.utils import parse_date, get_jY


_template_file = os.path.join(
    os.path.dirname(__file__),
    "sohemailer_templates",
    "sohemailer_template.htm"
)


CONFIG_DICT = {
    "passwd": "",
    "from": "",
    "to": [],
    "subject": "State of Health alert",
    "alert_filepathformat": "",
    "station_ids": [],
    "sohpars": [],
}


def send_email(from_="", to_="", passwd="", subject="", content=""):
    """
    Send email using 'smtp.gmail.com' smtp server.

    :type from\_: str
    :param from\_: email address of the sender
    :type to\_: list[str]
    :param to\_: list of email address of recipients
    :type passwd: str
    :param passwd: sender email account password
    :type subject: str
    :param subject: email subject
    :type content: str
    :param content: message contents
    """
    if not to_:
        return

    msg = email.message.Message()
    msg['From'] = from_
    msg['Subject'] = subject
    msg['To'] = to_
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(content)

    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(msg['From'], passwd)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()


def main(argv=None):
    """
    :type argv: list
    :param argv: command line arguments
    """
    parser = ArgumentParser(prog='polyfemos-sohemailer',
                            description=__doc__.strip())
    parser.add_argument('path', type=str,
                        help='YAML file containing emailing configuration')
    parser.add_argument('-d', '--date', type=str, default="",
                        help='Alert file date, in format YEAR-JULDAY, '
                             'YEAR-MONTH-DAY, or '
                             'empty for current date.')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Shows what the command would have done without '
                             'actually doing anything.')
    args = parser.parse_args(argv)

    dry_run = args.dry_run
    path = args.path
    date_ = args.date

    yaml_config = fileutils.load_yaml(path)
    if yaml_config is None:
        print("No valid YAML file given.")
        return

    CONFIG_DICT.update(yaml_config)

    fpf = to.filepath(CONFIG_DICT["alert_filepathformat"])

    date_ = parse_date(date_)
    datestr = date_.strftime("%Y.%m.%d %H:%M:%S")
    julday, year = get_jY(date_)
    infolines = ["Currently active alerts for date {}".format(datestr)]

    sohdict = get_sohdict(CONFIG_DICT["station_ids"], year, julday, fpf)
    alerts = sohdict["alerts"]

    msglines = []
    _product = itertools.product(
        CONFIG_DICT["station_ids"], CONFIG_DICT["sohpars"])
    for station_id, parname in _product:
        alert = alerts.get(station_id + parname, "")
        msgline = "{:<10} {:<30}".format(station_id, parname)
        # Only currently active alerts will be added to message.
        if alert == "2":
            print(msgline)
            msglines.append(msgline.replace(' ', "&nbsp;"))

    # Email is sent if there are currently active alerts
    if len(msglines) > 0:
        msglines = infolines + msglines
        email_content = \
            fileutils.render_template(_template_file, {"msglines": msglines})

        if dry_run:
            print("\nEmail contents\n")
            print(email_content)
            return

        for to_ in CONFIG_DICT["to"]:
            print("Sending email to '{}'".format(to_))
            send_email(
                to_=to_,
                from_=CONFIG_DICT["from"],
                passwd=CONFIG_DICT["passwd"],
                subject=CONFIG_DICT["subject"],
                content=email_content,
            )
    else:
        print("No alerts, no email sent")


if __name__ == "__main__":
    main()
