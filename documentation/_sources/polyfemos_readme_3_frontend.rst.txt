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



.. _Frontend:

Frontend
========


Web pages of polyfemos web
--------------------------

List of sites:

- :ref:`Index`
- :ref:`Home`
- :ref:`SOHTable`
- :ref:`SOHMap`
- :ref:`DataCoverageBrowser`
- :ref:`DataCoverageImage`
- :ref:`StatisticsSummary`
- :ref:`PlotBrowser`
- :ref:`AlertHeatTable`
- :ref:`Documentation`


Most sites of the polyfemos provide system time information
on low left corner. The time information is provided in UTC and in local
timezones. In addition, the day of the year (ordinal) is shown.



.. _Index:

Index
^^^^^


Short description of polyfemos web for random visitors



.. _Home:

Home
^^^^


Navigation page of polyfemos web



.. _SOHTable:

SOH Table
^^^^^^^^^


The state of health alert files ('\*.alert') are read to produce the table.

Each cell in the table provides a link to the corresponding plot.

The alert status of each station and state of health parameter combination is
shown in state of health table. The date is selectable. In addition to date 
dropdown menu, it is also possible to navigate between different dates using
'+date' and '-date' buttons which both add or subtract 1 day.   

If 'Show all' check box is checked, state of health parameters with visibities
1 and 2 are shown. If not, only parameters with visibility 1 are shown.
Visibilities are set in YAML files, see :ref:`FrontendConfiguration`.

If 'Realtimeness filter' check box is checked, outdated alerts are not shown
(Grey). The time limit for exclusion is selectable using 'Realtimeness limit'
text field. The field takes a limit as seconds. If the timestamp value
'last_dp_ts' in the alert file is smaller than the current polyfemos web server
time minus the 'Realtimeness limit', the alert data is considered to be
outdated.


Cell colors with explanations:

- Red, alert currently on, (threshold is broken)
- Yellow, alert has been on during the day, (threshold has been broken)
- Green, no alerts
- Grey, the data is outdated
- Very Light Grey, no data available



.. _SOHMap:

SOH Map
^^^^^^^

Coordinates and the EPSG information are read from the '\*.stf' files
(ESPG, LOCX, and LOCY header fields).
`OziExplorer <https://www.oziexplorer4.com/w/>`_ 
'\*.map' file and the corresponding '\*.png' image must be provided
in the folder: 'web_static', which located in folder '~/polyfemos' if the
default convention was followed during setup.

The example file 'northern_finland.map', was created using
`fetch_map <https://olammi.iki.fi/sw/fetch_map/>`_. 
More information about the '\*.map' file in
:func:`~polyfemos.util.coordinator.transform_from_ozi_map`.

In the State of health map, 
the inner most circle consists of priority 1 parameters, the
center circle priority 2 and the outer most circle consists of parameters with
priorities 3 and 4.



.. _DataCoverageBrowser:

Data Coverage Browser
^^^^^^^^^^^^^^^^^^^^^

Creates a datacoverage image incorporating selected stations and data channels
and with selected time interval. Uses userdefined scanning function, see
:ref:`FrontendConfiguration`. The available functions can be reviewed in
:func:`~polyfemos.front.userdef.get_datacoveragebrowser_func`.



.. _DataCoverageImage:

Data Coverage Image
^^^^^^^^^^^^^^^^^^^

If backend is set to create a data coverage image in realtime, this site
will show the image.




.. _StatisticsSummary:

Statistics Summary
^^^^^^^^^^^^^^^^^^


Available values and their units in statistics summary 

+--------------+-------+---------------------------------------------------------------------------------------+
| Abbreviation | Unit  | Description                                                                           |
+==============+=======+=======================================================================================+
| Median       | \*    | median                                                                                |
|              |       |                                                                                       |
+--------------+-------+---------------------------------------------------------------------------------------+
| Min          | \*    | minimum                                                                               |
|              |       |                                                                                       |
+--------------+-------+---------------------------------------------------------------------------------------+
| Max          | \*    | maximum                                                                               |
|              |       |                                                                                       |
+--------------+-------+---------------------------------------------------------------------------------------+
| Mean         | \*    | mean                                                                                  |
|              |       |                                                                                       |
+--------------+-------+---------------------------------------------------------------------------------------+
| SD           | \*    | standard deviation                                                                    |
|              |       |                                                                                       |
+--------------+-------+---------------------------------------------------------------------------------------+
| CV%          | %     | `coefficient of variation <https://en.wikipedia.org/wiki/Coefficient_of_variation>`_  |
|              |       |                                                                                       |
+--------------+-------+---------------------------------------------------------------------------------------+
| TIB%         | %     | percentage of datapoints which break the threshold, non existed (for example nan      |
|              |       | values are not counted                                                                |
+--------------+-------+---------------------------------------------------------------------------------------+
| Lower        | \*    | lower alert threshold                                                                 |
|              |       |                                                                                       |
+--------------+-------+---------------------------------------------------------------------------------------+
| Higher       | \*    | higher alert threshold                                                                |
|              |       |                                                                                       |
+--------------+-------+---------------------------------------------------------------------------------------+
| UNIT         | \-    | \* In units defined in this field, retrieved from '\*.stf' file header                |
|              |       |                                                                                       |
+--------------+-------+---------------------------------------------------------------------------------------+



If 'Remove irrational values' check box is checked, irrational values
are remove before value calculations. The lower and higher limit for 
irrational limits should be defined in '\*.stf' file header. In addition,
data outliers can possibly be removed using 'Advanced outlier removal'
option. 

The used functions for removing outliers with different station and sohpar
combinations can be defined in function  YAML files. Information about used
outlier removal function can be documented by user in YAML summary
outlierremfunc info. The available outlier removal functions are listed in
:func:`~polyfemos.front.userdef.get_outlierremfunc`. See
:ref:`FrontendConfiguration` for more info.

The different header information for the summary may be selected using
'Headerdate' dropdown menu. 

The data for the summary can read from '\*.csv' or '\*.stf' files.
The used input file format is selected using 'Read from' dropdown menu. 

The resulting summary table is either outputted into the site or downloaded
as csv file. Check 'Download csv' check box to download the summary as csv.






.. _PlotBrowser:

Plot Browser
^^^^^^^^^^^^


In the Plot Browser view the user may plot different state of health
parameters. The user may select from different station and the parameter
combinations, and with different timespans. In addition, the headerdate is
selectable in order to choose between different header information of the
'\*.stf' files.

By default, the data for the plot is read from the '\*.stf' files. The input
file format may be changed to csv using 'Read from' dropdown menu.  
In order to create 'NEZ' offset plots,
the data for the offset transformations is  read from '\*.stf' files.

Alert line (horizontal bright red lines) and unit
information is read from the header of '\*.stf' files.

If 'Remove irrational values' is checked, datapoints with irrational
y values are removed. Upper and lower limit for irrational values
is defined in '\*.stf' file header.

If 'Remove indetical values' is checked, datapoints with identical
x (time) and y values are removed.

If 'Track data length' is checked, the amount of datapoints and 'nan' values
is tracked after each dataprocessing step during the creation of the plot.
Results are printed to the right of the plot after the plot is ready.

In order to decimate the shown data, check the 'Decimate' check box. 
The maximum amount of data points after decimation is set to 10000. This is a
fixed value. 

Advanced outlier removal options may used to remove outlying datapoints from
the data. If 'None' is selected, outliers are not removed. (Irrational values
are still removed if the corresponding check box is checked.) Three different
functions to remove outliers are provided. Each function option has input
fields for setting the function arguments. See
:mod:`~polyfemos.data.outlierremover` for more info about the outlier removal
functions and their arguments.



.. _AlertHeatTable:

Alert Heat Table
^^^^^^^^^^^^^^^^

The alert heat table is very similar to the :ref:`SOHTable`. In alert heat
map, a time interval is chosen and the '\*.alert' files during these days are
read.

For each day each station and sohpar combinations will receive 'points'.
If the alert file for the day is available, the station-sohpar combination 
will receive at most 2 points. By default points are set as follows: 
1 point if the threshold has been broken during the day and 2 points if the
threshold was broken at the end of the day. The received points can be
adjusted using 'Points per tib' and 'Points per thbb' dropdown menus.

The total 'theoretical' maximum value of points is increased by 
2 for each day in which the
alert file was available. Hovering over the cell in the table
will provide total point count, the 'theoretical' maximum and 
the ratio (percents) between the aforementioned values. 

'Locarithmic color' ckeck box can be used to make lesser color values
more prominent.



.. _Documentation:

Documentation
^^^^^^^^^^^^^

This very site/document you are reviewing right now.




Keyboard Shortcuts
------------------


+-----------+------------------+---------------------------------------------+
| Key       | Works in         | Description                                 |
+===========+==================+=============================================+
| q         | 1,2,3,4,5,6,7,8  | Go to :ref:`Home`                           |
+-----------+------------------+---------------------------------------------+
| w         | 1,2,3,4,5,6,7,8  | Go to :ref:`SOHTable`                       |
+-----------+------------------+---------------------------------------------+
| e         | 1,2,3,4,5,6,7,8  | Go to :ref:`SOHMap`                         |
+-----------+------------------+---------------------------------------------+
| r         | 1,2,3,4,5,6,7,8  | Go to :ref:`PlotBrowser`                    |
+-----------+------------------+---------------------------------------------+
| t         | 1,2,3,4,5,6,7,8  | Go to :ref:`DataCoverageBrowser`            |
+-----------+------------------+---------------------------------------------+
| y         | 1,2,3,4,5,6,7,8  | Go to :ref:`DataCoverageImage`              |
+-----------+------------------+---------------------------------------------+
| u         | 1,2,3,4,5,6,7,8  | Go to :ref:`StatisticsSummary`              |
+-----------+------------------+---------------------------------------------+
| i         | 1,2,3,4,5,6,7,8  | Go to :ref:`AlertHeatTable`                 |
+-----------+------------------+---------------------------------------------+
| o         | 1,2,3,4,5,6,7,8  | Go to :ref:`Documentation`                  |
+-----------+------------------+---------------------------------------------+
| p         | 1,2,3,4,5,6,7,8  | Go to :ref:`Index`                          |
+-----------+------------------+---------------------------------------------+
| backspace | 1,2,3,4,5,6,7,8  | Go back                                     |
+-----------+------------------+---------------------------------------------+
| enter     | 2,4,5,7,8        | Submit form                                 |
+-----------+------------------+---------------------------------------------+
| left arrow| 2                | Substract a day                             |
|           |                  |                                             |
+-----------+------------------+---------------------------------------------+
|right arrow| 2                | Add a day                                   |
|           |                  |                                             |
+-----------+------------------+---------------------------------------------+


1.  :ref:`Home`
2.  :ref:`SOHTable`
3.  :ref:`SOHMap`
4.  :ref:`PlotBrowser`
5.  :ref:`DataCoverageBrowser`
6.  :ref:`DataCoverageImage`
7.  :ref:`StatisticsSummary`
8.  :ref:`AlertHeatTable`
9.  :ref:`Documentation`
10. :ref:`Index`



Restrictions
------------


| Index                   [1]
| Home                    [2]
| SOH Table               [2]
| SOH Map                 [2]
| Data Coverage Image     [2]
| Plot Browser            [3]
| Data Coverage Browser   [4]
| Alert Heat Table        [4]
| Statistics Summary      [4]

1.  full access for all
2.  full access for all registered users
3.  limited access for users with access level 2 and 3
4.  limited access for users with access level 2 


Access levels:

1.  full access
2.  full access with some limitations
3.  limited access


In Plot Browser, users with access level > 1, can not uncheck 'Decimate' and
'Remove indentical values' checkboxes. In addition, users with this access
level may only plot at most 2 plots at once, with maximum timespan of 35 days.

In all limited sites, users with limitations may only make one function call
at the time.



.. _FrontendConfiguration:

Configuration
-------------

Frontend configuration is done using YAML (\*.yml) files. Global configuration
file should be found in location 'conf/front/global_config.yml'.

Each network included in polyfemos should have an own configuration file.
Network configuration files must be included in folder 'conf/front/networks',
and named '???_config.yml', ??? being the name of the network.




Global Configuration
^^^^^^^^^^^^^^^^^^^^

Keys in global config are:


.. rubric:: secret_key

The value is string defining the secret key for flask server.

.. code-block:: yaml
    
    secret_key: "ChangeThisImmediately!"


.. rubric:: network_codes

The value is a list defining all networks available in polyfemos web.

.. code-block:: yaml
    
    network_codes:
      - FN
      ...


.. rubric:: users

The value is a dictionary consisting of all allowed users. The value of each 
user is a dictionary defining the level of access as integer.

.. code-block:: yaml

    users:
      admin:
        access_level: 1
      user1:
        access_level: 2
      user2:
        access_level: 3
      ...


.. rubric:: paths

The value is dictionary defining all global paths, the value of each path
is a string.

.. code-block:: yaml

    paths:
      server_ip: "123.123.123.45"
      nginx_dir: "/etc/nginx"
      ...

+-----------------------+-----------------------------------------------------+
|  Global path key      |  Description                                        |
+=======================+=====================================================+
|  server_ip            |  IP address of the polyfemos server                 |
+-----------------------+-----------------------------------------------------+
|  server_name          |  name of the polyfemos server,                      |
|                       |  url without 'http://'                              |
+-----------------------+-----------------------------------------------------+
|  url                  |  Complete url of the polyfemos site                 |
+-----------------------+-----------------------------------------------------+
|  user                 |  Username of the user hosting polyfemos             |
+-----------------------+-----------------------------------------------------+
|  group                |  Usergroup name hosting polyfemos                   |
+-----------------------+-----------------------------------------------------+
|  working_dir          |  Directory containing all codes for polyfemos web   |
+-----------------------+-----------------------------------------------------+
|  nginx_dir            |  Directory for nginx files,                         |
|                       |  for example 'sites-available'                      |
|                       |  directory should be found here                     |
+-----------------------+-----------------------------------------------------+
|  env_dir              |  Directory of the used python/conda environment     |
+-----------------------+-----------------------------------------------------+
|  service_dir          |  Directory for polyfemos web service file           |
+-----------------------+-----------------------------------------------------+
|  passwd_file          |  File where user and password information           |
|                       |  is stored, '.htpasswd' for example                 |
+-----------------------+-----------------------------------------------------+
|  webusagelog_file     |  File were the information fo visiting users is     |
|                       |  logged                                             |
+-----------------------+-----------------------------------------------------+
|  nginx_log_dir        |  Directory where nginx logs are found               |
|                       |                                                     |
+-----------------------+-----------------------------------------------------+
|  uwsgi_log_dir        |  Directory where uwsgi logs,                        |
|                       |  Python's print command will output here            |
+-----------------------+-----------------------------------------------------+
|  ttf_file             |  Path to the truetype font file                     |
|                       |                                                     |
+-----------------------+-----------------------------------------------------+
|  doc_dir              |  Directory containing polyfemos documentation       |
|                       |                                                     |
+-----------------------+-----------------------------------------------------+




Network Configuration
^^^^^^^^^^^^^^^^^^^^^


.. rubric:: paths

The value is dictionary defining all network paths, the value of each path
is a string.

.. code-block:: yaml

    paths:
      dci_file: "FN_datacoverage_weekly.png"
      map_file: "northern_finland.png"


+-----------------------+-----------------------------------------------------+
|  Network path key     |  Description                                        |
+=======================+=====================================================+
|  dci_file             |  Name of the datacoverage image file,               |
|                       |  should be found in static folder                   |
+-----------------------+-----------------------------------------------------+
|  map_file             |  Name of the backbroung map image file for SOH map, |
|                       |  the OziExplorer '\*.map' file                      |
|                       |  should have the same name                          |
|                       |  as the png file, only different file extension.    |
+-----------------------+-----------------------------------------------------+


.. rubric:: filepathformats

The value is dictionary defining all dynamic network paths,  the value of each
path is a string.

When defining filepath formats it's possible to use :ref:`ReservedVariables`
in order to define dynamic filepaths.

.. code-block:: yaml

    filepathformats:
      rawdata: "~/polyfemos_example_data/&YEAR/&NETWORK/&STATION/&CHANNEL.D/&NETWORK.&STATION.*.&CHANNEL.D.&YEAR.&JULDAY"
      stf: "~/polyfemos/data_out/FN/sohtextfiles/&YEAR/&NETWORK/&STATION/&NETWORK.&STATION.&YEAR.&JULDAY"
      csv: "~/polyfemos/data_out/FN/sohcsvs/&YEAR/&NETWORK/&STATION/&PARNAME/&NETWORK.&STATION.&PARNAME.&YEAR"
      alert: "~/polyfemos/data_out/FN/sohalerts/&YEAR/&NETWORK/&STATION/&NETWORK.&STATION.&YEAR.&JULDAY"

+-----------------------+-----------------------------------------------------+
|  Filepathformat key   |  Description                                        |
+=======================+=====================================================+
|  stf                  |  Path to state of health text files (\*.stf)        |
|                       |                                                     |
+-----------------------+-----------------------------------------------------+
|  csv                  |  Path to state of health csv files (\*.csv)         |
+-----------------------+-----------------------------------------------------+
|  alert                |  Path to state of health alert files (\*.alert)     |
+-----------------------+-----------------------------------------------------+
|  rawdata              |  Path to raw data files                             |
+-----------------------+-----------------------------------------------------+



.. rubric:: station_ids

The value is a list of string values defining the station ids. Station id
consists of a network and a station code separated with a dot.

.. code-block:: yaml

    station_ids: [ 
      "FN.MSF",
      "FN.SGF",
      ...
    ]


.. rubric:: channel_codes

The value is a list of string values defining every available data channel
across all stations.

.. code-block:: yaml

    channel_codes: [
      "HHZ", "HHN", "HHE",
      "BHZ", "BHN", "BHE",
      "AE1", "AE2", "AE3",
      "GNS", "GLA", "GLO",
      ...
    ]


.. rubric:: sohpars

The value is a list of dictionaries. Each dictionary consists of  keys
``name``, ``group`` and ``visibility``. The value of ``name`` is the name of
the state of health parameter as a string, the value ``group`` is a name of
the state of health parameter group where the parameter is included and the
value ``visibility`` is a integer defining where the parameter is shown in
polyfemos web.

In :ref:`SOHMap`, :ref:`AlertHeatTable` and :ref:`SOHTable` parameters with
visibilities 1 and 2 are shown. In the latter, user may choose to only
parameters with visibility of 1. In :ref:`PlotBrowser` and
:ref:`StatisticsSummary` parameters with visibilities 1, 2 or 3 are
selectable. Parameters with other visibility values than mentioned above
are not shown anywhere in polyfemos web.

.. code-block:: yaml

    sohpars:
      - {name: Digitizer_input_voltage, group: Environment, visibility:  1}
      - {name: Timing_quality_HHZ,      group: Timing,      visibility:  2}
      ...


.. rubric:: ticklabels

The value is a dictionary consisting of parameter names as keys. Each value
of the dictionary is an another dictionary. In the innermost dictionary the
keys are integers and values are string values. 

Ticklabels are used in :ref:`PlotBrowser` to map discrete y-values into more
descriptive ones for y-axis tick labels.

.. code-block:: yaml

    ticklabels:
      GPS_status:
        0: "off (0)"
        1: "unlocked (1)"
        2: "locked (2)"
    ...


.. rubric:: definitions

The value is a dictionary consisting of the internal parameter names as keys.
The values of the dictionary are string values defining the user defined 
parameter name corresponding to the internal name.

In the example code block all the internal names are shown.

.. code-block:: yaml

    definitions:
      datarealtimeness: Data_realtimeness_HHZ
      offset_n: Offset_N
      offset_e: Offset_E
      offset_z: Offset_Z
      offset_u: Offset_U
      offset_w: Offset_W
      offset_v: Offset_V


.. rubric:: datacoveragebrowser_func

The value is a string representing the selected data coverage scanning
function. Available functions can be reviewed in
:func:`~polyfemos.front.userdef.get_datacoveragebrowser_func`.

The selected function is used in :ref:`DataCoverageBrowser`.

.. code-block:: yaml

    datacoveragebrowser_func: seismic_scanner


.. rubric:: summary_outlierremfunc_info

The value is a list of strings defining user defined info paragrahps in
:ref:`StatisticsSummary`. The user may write here the information concerning
the used outlier removal functions.

.. code-block:: yaml

    summary_outlierremfunc_info:
      - "Advanced outlier removing info"
      - "FN.ASDF, Vault_temperature, Lipschitz continuity"
      ...


.. rubric:: summary_outlierremfuncs

The value is a dictionary containing station id and parameter pairs as keys.
The station id and the parameter name are separated with a colon. The value of
the key is yet another dictionary consisting of key ``function`` which is the
name of the function as a string, selectable from
:func:`~polyfemos.front.userdef.get_outlierremfunc`. Other keys to this
dictionary are the keyword arguments for the function.

The defined outlier removal functions are used in :ref:`StatisticsSummary`.

.. code-block:: yaml

    summary_outlierremfuncs:
      FN.ASDF:Vault_temperature:
        function: lipschitz
        itern: 1
        klim: 0.00007
      ...


