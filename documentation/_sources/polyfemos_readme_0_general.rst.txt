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



General Notes
=============

:organization: Sodankylä Geophysical Observatory, University of Oulu
:copyright: University of Oulu, Sodankylä Geophysical Observatory
:date: 2019

The polyfemos package and its documentation is distributed under 
`GNU Lesser General Public License v3.0 or later
<https://spdx.org/licenses/LGPL-3.0-or-later.html>`_. Exceptions are listed
below.

The polyfemos package comes with ``sorttable.js`` table sorter by 
Stuart Langridge, <http://www.kryogenix.org/code/browser/sorttable/>. The
source file is not modified. The ``sorttable.js`` is provided under licence
<http://www.kryogenix.org/code/browser/licence.html>.

The 'northern_finland.png' example png map file is licensed as CC BY-SA
<https://creativecommons.org/licenses/by-sa/2.0/>. Copyright OpenStreetMap
contributors <https://www.openstreetmap.org/copyright>.

The data contained in folder 'polyfemos_example_data' is licenced under 'SGO
Data Licence Agreement, 8.11.2019'. The licence file
'SGO_DATA_LICENCE_AGREEMENT.txt' is provided with the data.

The polyfemos backend is made seismic studies in mind and currently supports
only seismic instruments. For the most part, the frontend (polyfemos web) on
the other hand should be compatible with anything that is capable of producing
'\*.stf', '\*.csv' and '\*.alert' files in suitable formats. See
:ref:`STFFormat`, :ref:`AlertFormat` and :ref:`CSVFormat` for more information.




Supported Hardware
------------------


The polyfemos (back and front) currently supports following hardware.


+------------+---------------+------------------------+---------------------+
|            |  Brand        |  Model                 |   Internal code     |
+============+===============+========================+=====================+
| Sensor     |  Nanometrics  |  Trillium 120PA        |   ``Trillium_120PA``|
|            +---------------+------------------------+---------------------+
|            |  Nanometrics  |  Trillium Posthole     |   ``Trillium_120PH``|
|            +---------------+------------------------+---------------------+
|            |  Nanometrics  |  Trillium Compact 120s |   ``Trillium_Co120``|
|            +---------------+------------------------+---------------------+
|            |  Streckeisen  |  STS-2                 |   ``STS-2``         |
+------------+---------------+------------------------+---------------------+
| Digitizer  |  Earth Data   |  PS6-24                |   ``PS6-24``        |
|            +---------------+------------------------+---------------------+
|            |  Earth Data   |  EDR-210               |   ``EDR-210``       |
|            +---------------+------------------------+---------------------+
|            |  Nanometrics  |  Centaur 3 channels    |   ``Centaur_3ch``   |   
|            +---------------+------------------------+---------------------+
|            |  Nanometrics  |  Centaur 6 channels    |   ``Centaur_6ch``   |
+------------+---------------+------------------------+---------------------+



Comments considering internal naming conventions
------------------------------------------------

+------------------+---------------------------------------------------------+
| Internal name    | Description                                             |
+==================+=========================================================+
| network_code\*   | Network code, e.g. "FN"                                 |
|                  |                                                         |
+------------------+---------------------------------------------------------+
| station_code\*   | Station code, e.g. "MSF"                                |
|                  |                                                         |
+------------------+---------------------------------------------------------+
| location_code\*  | Location code, usually empty or "00"                    |
|                  |                                                         |
+------------------+---------------------------------------------------------+
| channel_code\*   | Channel code, e.g. "HHZ"                                |
|                  |                                                         |
+------------------+---------------------------------------------------------+
| station_id       | Combination of network and station codes, e.g. "FN.MSF" |
|                  |                                                         |
+------------------+---------------------------------------------------------+
| sohpar_name,     | State of health parameter name,                         |
| parname          | e.g. "Digitizer_input_voltage"                          |
|                  |                                                         |
+------------------+---------------------------------------------------------+
| year             | Year                                                    |
|                  |                                                         |
+------------------+---------------------------------------------------------+
| julday           | Day of the year                                         |
|                  |                                                         |
+------------------+---------------------------------------------------------+


\* The 'code' is omitted in case of the reserved variables, see
Chapter :ref:`ReservedVariables`.

Polyfemos web and polyfemos frontend will be synonymous in the documentation.



Console scripts
---------------


Polyfemos provides next command line scripts

+----------------------+---------------------------------------------------------+
| Script alias         | Link to code                                            |
+======================+=========================================================+
| polyfemos-readconf   | :func:`polyfemos.back.main.readconf`                    |
|                      |                                                         |
+----------------------+---------------------------------------------------------+
| polyfemos-devserver  | :func:`polyfemos.scripts.devserver.main`                |
+----------------------+---------------------------------------------------------+
| polyfemos-rwt        | :func:`polyfemos.scripts.render_web_templates.main`     |
+----------------------+---------------------------------------------------------+
| polyfemos-tfp        | :func:`polyfemos.scripts.test_front_paths.main`         |
+----------------------+---------------------------------------------------------+
| polyfemos-secret_key | :func:`polyfemos.util.randomizer.get_secret_key`        |
+----------------------+---------------------------------------------------------+
| polyfemos-sohemailer | :func:`polyfemos.scripts.sohemailer.main`               |
+----------------------+---------------------------------------------------------+
| polyfemos-check      | :func:`polyfemos.scripts.check_output_files.main`       |
+----------------------+---------------------------------------------------------+


