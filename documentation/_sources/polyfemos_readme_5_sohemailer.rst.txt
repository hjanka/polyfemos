.. This file is part of Polyfemos.
..
.. Polyfemos is free software: you can redistribute it and/or modify it under
.. the terms of the GNU Lesser General Public License as published by the Free
.. Software Foundation, either version 3 of the License, or any later version.
..
.. Polyfemos is distributed in the hope that it will be useful, but WITHOUT ANY
.. WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
.. A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
.. details.
..
.. You should have received a copy of the GNU Lesser General Public License and
.. GNU General Public License along with Polyfemos. If not, see
.. <https://www.gnu.org/licenses/>.
..
.. Author: Henrik Jänkävaara
.. Copyright: 2019, University of Oulu, Sodankyla Geophysical Observatory
.. License: GNU Lesser General Public License v3.0 or later
..          (https://spdx.org/licenses/LGPL-3.0-or-later.html)



.. _SOHEmailer:

State of health emailer
=======================

The state of health emailer (:func:`~polyfemos.scripts.sohemailer.main`) can
be used to notify about the problems with stations and parameters via email.

Only currently active alert (value=2) are reported. The date of the alertfile
is selectable using an optional command line option, though.


Configuration
-------------

The emailer is configured using a YAML file. The file is passed as a command
line argument to the emailer.

Keys in the configuration file are:


.. rubric:: from

The value is a string defining the email sender

.. code-block:: yaml

    from: "soh.sender@example.com"


.. rubric:: passwd

The value is a string defining the password of the sender's email account.

.. code-block:: yaml

    passwd: "***************"
    

.. rubric:: to

The value is a list of string defining the email addresses of the recipients. 

.. code-block:: yaml

    to: [
      "some.recipient@example.com",
      ...
    ]


.. rubric:: subject

The value is a string describing the email subject.

.. code-block:: yaml

    subject: "State of Health alert"


.. rubric:: alert_filepathformat

The value is a string defining the dynamic alertfile path. When defining the
filepath format, it's possible to use :ref:`ReservedVariables`.

.. code-block:: yaml

    alert_filepathformat: "~/polyfemos/data_out/FN/sohalerts/&YEAR/&NETWORK/&STATION/&NETWORK.&STATION.&YEAR.&JULDAY"


.. rubric:: station_ids

The value is a list strings defining the selected station ids. Only
alerts corresponding these stations will be reported.

.. code-block:: yaml

    station_ids: [ 
      "FN.MSF",
      "FN.SGF",
      ...
    ]


.. rubric:: sohpars

The value is a list strings defining the selected state of health parameters.
Only alerts corresponding these parameters will be reported.

.. code-block:: yaml

    sohpars:
      - "Digitizer_input_voltage"
      - "Data_realtimeness_HHZ"

