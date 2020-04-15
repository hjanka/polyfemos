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



.. _Backend:

Backend
=======


.. _ConfigurationFiles:

Configuration Files
-------------------


The backend program execution (e.g. creation of sohtextfiles ['\*.stf'])  is
defined in '\*.conf' files. The definition is done using commands provided.
Line starts with command and is followed by appropriate amount of proper 
arguments. Arguments are separated by any number whitespaces. Each command
starts with command symbol (backslash, \'\\\\'). 

Each line not starting with command symbol, is considered comment line.
Additionally comment symbol ('#') is provided to comment more freely.
Whitepaces at the start of the line may be used for intendation.

Hint: Using Clojure syntax coloring with '\*.conf' files will highlight
the syntax quite nicely. Clojure comment symbol (';') can then be used
at the start of the lines. 




Available commands and their arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Available commands (Add command symbol before every command to use it):

+-----------------+-----------------------------------------------------------------+
| Command         |   Description                                                   |
+=================+=================================================================+
| :ref:`IMPORT`   |   import external '\*.conf' files                               |
+-----------------+-----------------------------------------------------------------+
| :ref:`FLAG`     |   define variables used in called functions etc.                |
+-----------------+-----------------------------------------------------------------+
| :ref:`VAR`      |   define variables used internally in '\*.conf' files           |
+-----------------+-----------------------------------------------------------------+
| :ref:`END`      |   exit scope                                                    |
+-----------------+-----------------------------------------------------------------+
| :ref:`START`    |   called optionally before RUN commands                         |
+-----------------+-----------------------------------------------------------------+
| :ref:`STOP`     |   called at the end of program execution                        |
+-----------------+-----------------------------------------------------------------+
| :ref:`RUN`      |   used to call functions                                        |
+-----------------+-----------------------------------------------------------------+
| :ref:`STATION`  |   define station, start station scope                           |
+-----------------+-----------------------------------------------------------------+
| :ref:`PAR`      |   define parameter, can only be called inside station scope     |
+-----------------+-----------------------------------------------------------------+


.. _IMPORT:

.. rubric:: IMPORT

| ``\IMPORT arg1``
| ``arg1`` - string, path to file  

Effectively, the command reads lines of the other file given as an argument.
In '\*.conf' files everything is in the same namespace. 


.. _FLAG:

.. rubric:: FLAG

| ``\FLAG arg1 arg2``
| ``arg1`` - string, name of the FLAG  
| ``arg2`` - type and value depends on the FLAG in question  

Defines values for FLAGs. FLAGs are used to setup values used by the program.
The available FLAGs and their types and default values are discussed in
:meth:`~polyfemos.back.interpreter.Interpreter._init_flags`.


.. _VAR:

.. rubric:: VAR

| ``\VAR arg1 arg2``
| ``arg1`` - string, name of the variable  
| ``arg2`` - string, value of the variable  

The variables can be used inside '\*.conf' files to apply same value to 
multiple locations. While assigning value to the variable, type of the value
is considered string. Note that the type of the variable should be suitable 
for the location where it is unpacked. Variable symbol ('$') is used to unpack
variables.

.. code-block:: text

    # assign something to variable 'filename'
    \VAR filename folder/file.conf  
    # unpack variable 'filename', the value contained in the variable  
    # should be suitable for the location where it is unpacked  
    # in this case, as the first argument of import command.  
    \IMPORT $filename  


.. _RUN:

.. rubric:: RUN

| ``\RUN arg1 argN``  
| ``arg1`` - string, name of the function to be executed  
| ``argN`` - the number of additional arguments and their types depends on the function.  

Command used to execute functions. :ref:`AvailableFunctions` discussed later.


.. _STATION:

.. rubric:: STATION

| ``\STATION arg1 arg2 arg3 arg4 arg5 arg6 arg7 arg8 arg9 arg10``
| ``arg1`` - string, network code, e.g. "FN"  
| ``arg2`` - string, station code, e.g. "MSF"  
| ``arg3`` - string, location code
| ``arg4`` - float, station Y coordinate  
| ``arg5`` - float, station X coordinate  
| ``arg6`` - string, EPSG code of station XY coordinates  
| ``arg7`` - string, digitizer  
| ``arg8`` - string, sensor  
| ``arg9`` - ordinal, station starttime  
| ``arg10`` - ordinal, station endtime   

Stations are idenfied by using the network and station codes.


.. _PAR:

.. rubric:: PAR

| ``\PAR arg1 arg2 arg3 arg4 arg5 arg6 arg7 arg8 arg9 arg10 arg11 arg12``
| ``arg1`` - string, parameter class  
| ``arg2`` - string, parameter name  
| ``arg3`` - string, parameter code  
| ``arg4`` - int, decimation_factor, the data is decimated according to this factor  
| ``arg5`` - float, scale, the parameter values are multiplied with this value  
| ``arg6`` - string, unit  
| ``arg7`` - floatlist, Y axis plotting limits  
| ``arg8`` - int, priority  
| ``arg9`` - function, function to invoke the alert  
| ``arg10`` - floatlist, lower and upper limit of totally irrational values  
| ``arg11`` - floatlist, alert limits, YELLOW, ORANGE, RED  
| ``arg12`` - filepath, filepath of the used file or folder, include the possible file extension

Parameters can only be defined inside station scope. STATION command invokes
the station scope. :ref:`AvailableParameterCodes` are discussed later.


.. _END:

.. rubric:: END

| ``\END``  
| no arguments

A command to exit scope


.. _START:

.. rubric:: START

| ``\START``
| no arguments

Saves program starttime to pickle file. For example, datacoverage parameters
used via :func:`~polyfemos.back.seismic.lumberjack.process_logs` function use
the starttime  and last starttime values.


.. _STOP:

.. rubric:: STOP

| ``\STOP``
| no arguments

Saves the current program starttime as the last starttime. The next time the
program will be executed, the previous starttime can be used.

----

There is no optional arguments, but there exists certain values that can be
used to define no existent or negligible values. These include:

.. code-block:: text

    NaN     # Equivalent to non-existent value
    []      # Empty list
    (False) # Function always returning False


Parameter and station definition example in chapter :ref:`HowToAddAStation`.




Symbols
^^^^^^^

+--------+----------------------------------------------------------------------------+
| Symbol | Description                                                                |                                                          
+========+============================================================================+
| \\     | Command symbol. Each command starts with this symbol. Each line not        |
|        | starting with the command symbol is considered comment line. Each          |
|        | operational line starts with command.                                      |
+--------+----------------------------------------------------------------------------+
| \#     | Comment symbol,                                                            |
|        | additionally each line that does not start with                            |
|        | the command symbol is considered comment line.                             |
+--------+----------------------------------------------------------------------------+
| \$     | Variable symbol,                                                           |
|        | using syntax '$var' extracts the value saved in the                        |
|        | variable named 'var', works internally in '\*.conf' files                  |
+--------+----------------------------------------------------------------------------+
| \&     | Reserved variable symbol. Each reserved variable starts with this symbol.  |
|        | Note that variables and reserved variables are totally different things,   |
|        | and their corresponding symbols are never used together.                   |
+--------+----------------------------------------------------------------------------+




Argument types
^^^^^^^^^^^^^^


.. rubric:: string

Almost anything goes. At the moment, whitespace and comment symbol
can not be included in the string.


.. rubric:: int

Integer number, as the value is read, it is first converted to float and then 
to int, which means that the decimals are just dropped of, e.g. "1.7 -> 1".


.. rubric:: bool

Boolean value, True of False, additionally similar boolean values as in 
python can be used, e.g. 0 and 1. 


.. rubric:: float

Floating point number, dot ('.') as a decimal separator


.. rubric:: floatlist

A list of floating point numbers. Separator is comma (','). Do not include
whitespaces.

.. code-block:: text

    [1,2.0,-1,5]


.. rubric:: strlist

A list of string values. Separator is comma (','). Do not include
whitespaces.

.. code-block:: text

    [MSF,OLKF,OUL,1,2]


.. rubric:: ordinal

String representing year and julian day. TODAY special variable can be used 
to define current date. At the program start timestamp and is saved and 
TODAY accessess this timestamp. See 
:class:`~polyfemos.almanac.ordinal.Ordinal` and 
:func:`~polyfemos.parser.typeoperator.ordinal` for more info.


.. rubric:: utcdatetime

String representing datetime value. TODAY special variable can be used to 
define current date. At the program start timestamp and is saved and 
TODAY accessess this timestamp. See 
:class:`~obspy.core.utcdatetime.UTCDateTime` and
:func:`~polyfemos.parser.typeoperator.utcdatetime` for more info.


.. code-block:: text

    # ordinal and utcdatetime examples: 
    2019-04  
    1970-1-1T12:12:00  
    &TODAY



.. rubric:: filepath

A dynamic filepath where reserved variables (YEAR, JULDAY etc., excluding 
TODAY) can be used to define varying parts. In the program 'filepath'
is a function. '/' is the root folder, '~' is the home folder and '.' is 
relative folder.


.. rubric:: staticfilepath

A constant filepath. In the definition of the filepath, 
reserved variables can not be used. 


.. rubric:: function

A function which can be used for simple arithmetic and boolean calculus.
Syntax is explained in the documentation of 
:func:`~polyfemos.parser.functionparser.function_from_str`.




Available FLAGs
^^^^^^^^^^^^^^^


see :meth:`~polyfemos.back.interpreter.Interpreter._init_flags` for available
FLAGs, their types and default values.



.. _AvailableFunctions:

Available functions with RUN command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


.. _process_logs:

.. rubric:: process_logs

| ``\RUN process_logs arg1 arg2 arg3 arg4 arg5``
| ``arg1`` - string, network code, e.g. "FN"
| ``arg2`` - string, station code, e.g. "MSF"
| ``arg3`` - ordinal, time interval startdate
| ``arg4`` - ordinal, time interval enddate
| ``arg5`` - strlist, list of parameter classes to be included 

The time interval includes both start and end dates.

See :meth:`polyfemos.back.interpreter.Interpreter.process_logs` and
:func:`polyfemos.back.seismic.lumberjack.process_logs` for more info.


.. rubric:: data_coverage_image

| ``\RUN data_coverage_image arg1 arg2 arg3 arg4 arg5 arg6 arg7``
| ``arg1`` - utcdatetime, starttime
| ``arg2`` - utcdatetime, endtime
| ``arg3`` - string, network code, e.g. "FN"
| ``arg4`` - strlist, list of station codes which are included in the image
| ``arg5`` - strlist, channels which are included in the image
| ``arg6`` - filepath, filepath to datafiles, include the possible file extension
| ``arg7`` - filepath, filepath of the output file(s), include the possible file extension

See :meth:`polyfemos.back.interpreter.Interpreter.data_coverage_image` and
:func:`polyfemos.back.seismic.scanner.data_coverage_image` for more info.



.. _AvailableParameterCodes:

Available parameter codes
^^^^^^^^^^^^^^^^^^^^^^^^^


The information about the state of health parameters from

- Nanometrics Inc., Centaur User Guide (2017)
- Earth Data, Instruction Manual for PS6-24 Seismic Datalogger (2004)


.. rubric:: For Centaur

+-------+----------------------------------------------------+----------------+
| Code  |  Description                                       | Unit           |
+=======+====================================================+================+
|  EX1  |  External SOH channel 1                            | Microvolts     |
+-------+----------------------------------------------------+----------------+
|  EX2  |  External SOH channel 2                            | Microvolts     |
+-------+----------------------------------------------------+----------------+
|  EX3  |  External SOH channel 3                            | Microvolts     |
+-------+----------------------------------------------------+----------------+
|  LCE  |  Absolute clock phase error                        | Microseconds   |
+-------+----------------------------------------------------+----------------+
|  LCQ  |  Clock quality                                     | Percents       |
+-------+----------------------------------------------------+----------------+
|  VCO  |  Timing oscillator control voltage                 | DAC counts     |
+-------+----------------------------------------------------+----------------+
|  VEC  |  Digitizer system current                          | Milliamps      |
+-------+----------------------------------------------------+----------------+
|  VM1  |  Sensor SOH channel 1, Offset voltages             | Microvolts     |
+-------+----------------------------------------------------+----------------+
|  VM2  |  Sensor SOH channel 2, Offset voltages             | Microvolts     |
+-------+----------------------------------------------------+----------------+
|  VM3  |  Sensor SOH channel 3, Offset voltages             | Microvolts     |
+-------+----------------------------------------------------+----------------+
|  VM4  |  Sensor SOH channel 4, Offset voltages             | Microvolts     |
+-------+----------------------------------------------------+----------------+
|  VM5  |  Sensor SOH channel 5, Offset voltages             | Microvolts     |
+-------+----------------------------------------------------+----------------+
|  VM6  |  Sensor SOH channel 6, Offset voltages             | Microvolts     |
+-------+----------------------------------------------------+----------------+
|  VPB  |  Digitizer buffer percent used                     |   Percents     |
+-------+----------------------------------------------------+----------------+
|  GNS  |  Number of GPS satellites used                     |   Pcs.         |
+-------+----------------------------------------------------+----------------+
|  GLA  |  GPS latitude                                      | Microdegrees   | 
+-------+----------------------------------------------------+----------------+
|  GLO  |  GPS longitude                                     | Microdegrees   |
+-------+----------------------------------------------------+----------------+
|  GEL  |  GPS elevation                                     | Micrometers    |
+-------+----------------------------------------------------+----------------+
|  GST  |  GPS status                                        | 0=off,         |
|       |                                                    | 1=unlocked,    |
|       |                                                    | 2=locked       |
+-------+----------------------------------------------------+----------------+
|  GPL  |  GPS PPL status                                    | 0=no lock,     |
|       |                                                    | 1=coarse lock, |
|       |                                                    | 2=fine lock,   |
|       |                                                    | 3=free running |
+-------+----------------------------------------------------+----------------+
|  VDT  |  Digitizer system temperature                      | Millidegrees   |
|       |                                                    | of Celsius     |
+-------+----------------------------------------------------+----------------+
|  VEI  |  Input system voltage                              | Millivolts     |
+-------+----------------------------------------------------+----------------+
|  GAN  |  GPS antenna status                                | 0=ok,          |
|       |                                                    | 1=no antenna,  |
|       |                                                    | 2=antenna short|
+-------+----------------------------------------------------+----------------+



.. rubric:: For Earth Data

The values are read from Earth Data state of health mseed files.
See :func:`~polyfemos.back.seismic.lumberjack.earthdata_mseed` and 
:func:`~polyfemos.back.seismic.lumberjack.get_earthdata_stream` for more info.

+-------+----------------------------------------------------+----------------+
| Code  |  Description                                       | Unit           |
+=======+====================================================+================+
|  AEP  |  16 bit phase error in 1 second pll                | Microseconds   |
+-------+----------------------------------------------------+----------------+
|  AE1  |  Supply voltage at input                           | Volts          |
+-------+----------------------------------------------------+----------------+
|  AE2  |  Supply current                                    | Milliamps      |
+-------+----------------------------------------------------+----------------+
|  AE3  |  Internal temperature                              | Degrees of     |
|       |                                                    | Celsius        |
+-------+----------------------------------------------------+----------------+
|  AE4  |  Supply voltage at remote connector/input          | Volts          |
+-------+----------------------------------------------------+----------------+
|  AE5  |  User input, offset                                | Volts          |
+-------+----------------------------------------------------+----------------+
|  AE6  |  User input, offset                                | Volts          |
+-------+----------------------------------------------------+----------------+
|  AE7  |  User input, offset                                | Volts          |
+-------+----------------------------------------------------+----------------+
|  AE8  |  Not in use                                        | Volts          |
+-------+----------------------------------------------------+----------------+


.. rubric:: For Earth Data LOG files

These values are read for the Earth Data LOG files, one value per day.
See :mod:`~polyfemos.back.seismic.edlogreader` for more info.

+-----------+--------------------------------------------------------+----------------+
| Code      |  Description                                           | Unit           |
+===========+========================================================+================+
| LOG.plle  | 16 bit phase error in 1 second pll                     |   Microseconds |
+-----------+--------------------------------------------------------+----------------+
| LOG.date  | Date, 8 numbers representing current date, "ddmmYYYY"  |                |
+-----------+--------------------------------------------------------+----------------+
| LOG.time  | Time, 6 numbers representing current time, "HHMMSS"    |                |
+-----------+--------------------------------------------------------+----------------+
| LOG.lat   | Latitude in WGS84 coordinates                          |                |
+-----------+--------------------------------------------------------+----------------+
| LOG.long  | Longitude in WGS84 coordinates                         |                |
+-----------+--------------------------------------------------------+----------------+
| LOG.hdng  | Heading                                                |   unknown      |
+-----------+--------------------------------------------------------+----------------+
| LOG.vel   | Velocity over ground                                   |   unknown      |
+-----------+--------------------------------------------------------+----------------+
| LOG.mva   | Magnetic variation                                     |   unknown      |
+-----------+--------------------------------------------------------+----------------+


.. rubric:: For data files

These values are read from the data mseed files. 'xxx' is the data channel
e.g. 'HHZ'.

+-----------+------------------------------------------------------------------+----------------+
| Code      |  Description                                                     | Unit           |
+===========+==================================================================+================+
| xxx       | [not in use] Raw data                                            |                |
+-----------+------------------------------------------------------------------+----------------+
| xxx.TQ    | Timing quality,                                                  | Percents       |
|           | :func:`~polyfemos.back.seismic.lumberjack.data_timing_quality`   |                |
+-----------+------------------------------------------------------------------+----------------+
| xxx.TSE   | Timestamp error,                                                 | Seconds        |
|           | :func:`~polyfemos.back.seismic.lumberjack._data_timestamp_error` |                |
+-----------+------------------------------------------------------------------+----------------+


.. rubric:: Data coverage codes 

See :func:`~polyfemos.back.seismic.lumberjack._data_coverage` and
:func:`~polyfemos.back.seismic.lumberjack.data_coverage` for more info.


+-----------+--------------------------------------------------------+----------------+
| Code      |  Description                                           | Unit           |
+===========+========================================================+================+
| xxx.DCD   | Data coverage from the start of the day                | Percents       |
+-----------+--------------------------------------------------------+----------------+
| xxx.DCL   | Data coverage from last program start                  | Percents       |
+-----------+--------------------------------------------------------+----------------+


.. rubric:: Data timing quality codes using daily obspy 

:func:`~obspy.io.mseed.util.get_flags` function. See
:func:`~polyfemos.back.seismic.lumberjack.data_timing_quality_obspy_daily` for
:more info.

+-----------+--------------------------------------------------------+----------------+
| Code      |  Description                                           | Unit           |
+===========+========================================================+================+
| xxx.TQMIN | Daily timing quality minimum                           | Percents       |
+-----------+--------------------------------------------------------+----------------+
| xxx.TQMAX | Daily timing quality maximum                           | Percents       |
+-----------+--------------------------------------------------------+----------------+
| xxx.TQAVE | Daily timing quality average                           | Percents       |
+-----------+--------------------------------------------------------+----------------+
| xxx.TQMED | Daily timing quality median                            | Percents       |
+-----------+--------------------------------------------------------+----------------+
| xxx.TQLOQ | Daily timing quality lower quartile                    | Percents       |
+-----------+--------------------------------------------------------+----------------+
| xxx.TQUPQ | Daily timing quality upper quartile                    | Percents       |
+-----------+--------------------------------------------------------+----------------+




.. _ReservedVariables:

Reserved variables
^^^^^^^^^^^^^^^^^^

+----------+-------------------------------------------------------+
| Reserved |                                                       | 
| variable |  Description                                          |
+==========+=======================================================+
| Reserved variables for constructing dynamic filepaths            |
+----------+-------------------------------------------------------+
| YEAR     |  Value from timevalue definition                      |
|          |  (e.g. from :ref:`process_logs` function arguments)   |
+----------+-------------------------------------------------------+
| JULDAY   |  Value from timevalue definition                      |
|          |  (e.g. from :ref:`process_logs` function arguments),  |
|          |  Day of the year                                      |
+----------+-------------------------------------------------------+
| JULDAY_ZP|  Value from timevalue definition                      |
|          |  (e.g. from :ref:`process_logs` function arguments)   |
|          |  Day of the year as a zero-padded number, e.g. '014'  |
+----------+-------------------------------------------------------+
| NETWORK  |  Value from :ref:`STATION` definition,                |
|          |  network code                                         |
+----------+-------------------------------------------------------+
| STATION  |  Value from :ref:`STATION` definition,                |
|          |  station code                                         |
+----------+-------------------------------------------------------+
| LOCATION |  Value from :ref:`STATION` definition,                |
|          |  location code                                        |
+----------+-------------------------------------------------------+
| CHANNEL  |  Value from :ref:`PAR` definition,                    |
|          |  channel code                                         |
+----------+-------------------------------------------------------+
| PARNAME  |  Value from :ref:`PAR` definition,                    |
|          |  state of health parameter name                       |
+----------+-------------------------------------------------------+
| Other reserved variables                                         |
+----------+-------------------------------------------------------+
| TODAY    |  Reserved variable that can be used to define         |
|          |  timevalues corresponding to the year                 |
|          |  and julian date of the current system time.          |
|          |                                                       |
+----------+-------------------------------------------------------+


When using reserved values, included reserved variable symbol ('&') in front
of the variable.

.. code-block:: text

    &TODAY
    &CHANNEL


.. _STFFormat:

Sohtextfile Format
------------------


The sohtextfile format ('\*.stf') focuses on human readability. In a
sohtextfile, all state of health parameters of a one station are stored, one
day per file. Each file consists of header block and data block, both blocks
are optional, but recommended for obvious reasons. If header is provided, it
must be defined before the data block.

The first line of the header block (and the sohtextfile) should be 'HEADER'.
The header block ends to 'DATA'-line.

'HEADER'-line is followed by all of the header fields and values. Each field
is a key-value pair separated with a whitespace. If the value is a list, the
list values are separated with comma (without any whitespaces). Floating point
number decimal separator is a dot '.'. If value does not exist the field can
be left out of the  header or the value can be set to 'NaN' or 'nan'.

The filename should contain network and station codes, year and julian day e.g.
``FN.MSF.2019.296.stf``.


+--------------+------------------------------------------------------------------+
| Header field |  Description                                                     |
+==============+==================================================================+
|                 Station specific header fields                                  |  
+--------------+------------------------------------------------------------------+
| ID           |  arbitrary identifier for the station,                           |  
|              |  recommended ID is 'NETWORK.STATION'                             |  
+--------------+------------------------------------------------------------------+
| NETWORK      |  network of the station                                          |  
+--------------+------------------------------------------------------------------+
| STATION      |  name of the station                                             |  
+--------------+------------------------------------------------------------------+
| LOCATION     |  location of the station how it is in the mseed files,           |  
|              |  usually empty ('NaN') or '00'.                                  |  
+--------------+------------------------------------------------------------------+
| SENSOR       |  sensor used in the station                                      |  
+--------------+------------------------------------------------------------------+
| DIGITIZER    |  digitizer used in the station                                   |  
+--------------+------------------------------------------------------------------+
| STARTTIME    |  utcdatetime compatible string, the information of the station   |  
|              |  is valid starting from this date                                |  
+--------------+------------------------------------------------------------------+
| ENDTIME      |  utcdatetime compatible string, the information of the station   |  
|              |  is not valid after this date                                    |  
+--------------+------------------------------------------------------------------+
| LOCY         |  station's y-coordinate                                          |  
+--------------+------------------------------------------------------------------+
| LOCX         |  station's x-coordinate                                          |  
+--------------+------------------------------------------------------------------+
| EPSG         |  epsg number of the used coordinate system (LOCY, LOCX),         |  
|              |  see 'https://spatialreference.org/ref/' for coordinate systems  |  
|              |  and their EPSG numbers.                                         |  
+--------------+------------------------------------------------------------------+
|                 Parameter specific header fields                                |  
+--------------+------------------------------------------------------------------+
| UNIT         |  the unit of the parameter's (y) values                          |  
+--------------+------------------------------------------------------------------+
| PRIORITY     |  the parameter's importance in case of malfunction               |  
+--------------+------------------------------------------------------------------+
| PLOTLIMS     |  list of two values, plotting range of the parameter,            |  
|              |  lower and higher limit.                                         |  
+--------------+------------------------------------------------------------------+
| IRLIMS       |  list of two values, limits for irrational values,               |  
|              |  lower and higher limit.                                         |  
|              |  If value is within this interval,                               |  
|              |  the value is considered reasonable.                             |  
+--------------+------------------------------------------------------------------+
| RED          |  list of two values, the highest priority alert limit,           |  
|              |  lower and higher limit.                                         |  
+--------------+------------------------------------------------------------------+
| ORANGE       |  list of two values, the intermediate priority alert limit,      |  
|              |  lower and higher limit.                                         |  
+--------------+------------------------------------------------------------------+
| YELLOW       |  list of two values, the lowest priority alert limit,            |  
|              |  lower and higher limit.                                         |  
|              |                                                                  |  
+--------------+------------------------------------------------------------------+


Station specific header fields are defined as follows:

.. code-block:: text

    ID FN.MSF
    NETWORK FN
    STATION MSF 

Parameter specific header field keys are are composed and defined as follows:

.. code-block:: text

    Parameter_name_UNIT NaN


Parameter name may have underscores but not whitespaces. The field name is
applied after the parameter name. Both are joined together with an underscore.


.. rubric:: Header example

.. code-block:: text

    HEADER 
    ID FN.MSF
    NETWORK FN
    STATION MSF
    LOCATION NaN
    SENSOR STS-2
    DIGITIZER PS6-24
    STARTTIME 1970-01-01T12:12:00.000000Z
    ENDTIME 2100-01-01T00:00:00.000000Z
    LOCY 7311537.718
    LOCX 592903.937
    EPSG 3067
    Timing_quality_BHZ_UNIT %
    Timing_quality_BHZ_PRIORITY 2
    Timing_quality_BHZ_PLOTLIMS -10,110
    Timing_quality_BHZ_IRLIMS 0,100
    Timing_quality_BHZ_YELLOW 95.0,NaN
    Timing_quality_BHZ_ORANGE 90.0,NaN
    DATA


After header block follows data block. 
The first line of the data block must be 'DATA'.
Each line in data block has 3 to 4 values separated with whitespaces.

Values from left to right are

1.  Timestamp as utcdatetime compatible string

2.  Parameter name

3.  Parameter value as floating point number dot as decimal separator.

4.  An optional field in which arbitrary values may be comprised.
    The syntax of this field follows python dictionary syntax.  


.. rubric:: Data example

.. code-block:: text

    DATA 
    2019-07-16T00:22:02.143940Z   Data_coverage_day_HHZ         91.6965216954                 {'starttime':'2019-07-16T00:00:00.000000Z'}
    2019-07-16T00:22:02.143940Z   Data_realtimeness_HHZ         0.0                           {'starttime':'2019-07-16T00:21:02.149581Z'}
    2019-07-16T00:20:05.550000Z   Timing_quality_HHZ            100.0
    2019-07-16T00:00:01.000000Z   Longitude                     23.964
    2019-07-16T00:00:01.000000Z   Latitude                      67.2347
    2019-07-16T00:11:56.000000Z   Timing_error                  5.0
    2019-07-16T00:14:03.000000Z   Digitizer_input_voltage       13.3687777778
    2019-07-16T00:13:34.000000Z   Digitizer_input_current       0.0
    2019-07-16T00:13:34.000000Z   Digitizer_temperature         34.2
    2019-07-16T00:00:00.000000Z   Offset_U                      nan
    2019-07-16T00:00:00.000000Z   Offset_W                      nan
    2019-07-16T00:17:23.000000Z   Offset_V                      -0.093



.. _AlertFormat:

Alert file Format
-----------------

The state of health alert files are actually semicolon separated csv files. The
data is in 5 columns, which are from leaft to right, station id, parameter
name, alert status, priority and the UTC timestamp (Unix timestamp in seconds)
of the last datapoint. Priorities range between 1 to 4, from highest to lowest.
Alert files should contain data of one day each.

The alert status is a number from 0 to 2, or 'nan'.

The filename should contain network and station codes, year and julian day e.g.
``FN.MSF.2019.296.alert``.



+--------------+--------------------------------------------------------------+
| Alert status | Description                                                  |
+==============+==============================================================+
| 0            | No alerts during this day                                    |
+--------------+--------------------------------------------------------------+
| 1            | There has been alert previously this day                     |
+--------------+--------------------------------------------------------------+
| 2            | The alert is currently on                                    |
+--------------+--------------------------------------------------------------+
| nan          | No data available                                            |
+--------------+--------------------------------------------------------------+


.. code-block:: text

    station_id;parameter;alert;priority;last_dp_ts
    FN.MSF;Timing_quality_HHZ;1;2;1546387194.2
    FN.MSF;Longitude;0;2;1546300800.0
    FN.MSF;Latitude;0;2;1546300800.0
    FN.MSF;Timing_error;1;2;1546387201.0
    FN.MSF;Digitizer_input_voltage;0;1;1546387825.0
    FN.MSF;Digitizer_input_current;0;4;1546387360.0
    FN.MSF;Digitizer_temperature;0;4;1546387857.0
    FN.MSF;Offset_U;0;3;1546387531.0
    FN.MSF;Offset_W;2;3;1546387433.0
    FN.MSF;Offset_V;0;3;1546387426.0



.. _CSVFormat:

State of health CSV Format
--------------------------

The file is a semicolon separated csv file, with at most 3 columns. The file 
contains time series data of one parameter for one year. The first column is a
UTC timestamp in seconds (Unix timestamp) and the second column is the data
value. Unit of the data in square brackets in file header. The third column (z)
is optional and contains an arbitrary amount of additional values in format
following python dictionary syntax.

The CSV format is an alternative to sohtextfile format. It is designed for
smoother user experience in polyfemos web. The usage of CSV is optional and
every feature is availble using only sohtextfiles.

The filename should contain network and station codes, parameter name and year
e.g. ``FN.MSF.Data_coverage_day_HHZ.2019.csv``.


.. code-block:: text

    utctimestamp;value [%];z
    1570629909.519853;0.0;{'starttime':'2019-10-09T00:00:00.000000Z'}
    1570776939.7208266;0.0;{'starttime':'2019-10-11T00:00:00.000000Z'}
    1571819578.5990593;0.0;{'starttime':'2019-10-23T00:00:00.000000Z'}






