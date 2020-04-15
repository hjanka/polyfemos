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



.. _HowToAddAStation:

How to add a station
====================



This guide will provide a simplified walkthrough on how to add
a station for monitoring purposes. In this example, station "FN.MSF"
will created and 'process_logs' function will be used to create
'\*.stf', '\*.alert' and '\*.csv' files. In addition, the station
will be added to the web side of polyfemos (front). 


If other stations have been defined previously and the new station shares many 
properties (for example same digitizer and location of data files) with 
previous stations, only steps marked with 4 \*-symbols might be needed.



1.  Locate the '\*.conf' files, where stations, parameters, filepaths
    and executed functions are defined.
    In this case, there is 3 configuration files:

    - 'conf/back/FN/driving_instructions.conf'
    - 'conf/back/FN/folders.conf'
    - 'conf/back/FN/stations.conf'

    All files are equal. 'folders.conf' and 'stations.conf' are imported
    into 'driving_instruction.conf' file.

    The program is executed using appropriate wrapper script.
    In this case, 'conf/back/FN/wrapper.sh'


2.  In 'folders.conf', check if FLAGs 'sohtextfilepath', 'sohalertpath' and 
    'sohcsvpath' are defined correctly. Do not use relative paths. These are 
    the output filepaths of the corresponding file format.

    .. code-block:: text

        \FLAG sohtextfilepath ~/polyfemos/data_out/FN/sohtextfiles/&YEAR/&NETWORK/&STATION/&NETWORK.&STATION.&YEAR.&JULDAY.stf
        \FLAG sohalertpath    ~/polyfemos/data_out/FN/sohalerts/&YEAR/&NETWORK/&STATION/&NETWORK.&STATION.&YEAR.&JULDAY.alert
        \FLAG sohcsvpath      ~/polyfemos/data_out/FN/sohcsvs/&YEAR/&NETWORK/&STATION/&PARNAME/&NETWORK.&STATION.&PARNAME.&YEAR.csv


3.  In 'folders.conf', check if FLAG 'execution_time_file' is defined 
    correctly. The FLAG is needed if any features requiring the program
    start time information are used, e.g. codes 'DCD', 'DCL' and 'TSE'.

    .. code-block:: text

        \FLAG execution_time_file conf/back/FN/program_execution_times.pkl


4.  For convenience, define filepath variables to be used with parameter 
    definitions. Suggested location is 'folders.conf' file. 
    These are filepath to the parameter specific data files.

    .. code-block:: text

        \VAR ED_log_path /path/to/raw/data/&YEAR/&NETWORK/&STATION/&CHANNEL.L/&NETWORK.&STATION.&LOCATION.&CHANNEL.L.&YEAR.&JULDAY
        \VAR Data_path   /path/to/raw/data/&YEAR/&NETWORK/&STATION/&CHANNEL.D/&NETWORK.&STATION.&LOCATION.&CHANNEL.D.&YEAR.&JULDAY


5.  In 'driving_instructions.conf' file, check file writing FLAGs. These 
    FLAGs define is certain output files are created.

    .. code-block:: text

        \FLAG write_sohalertfile True  # boolean, defaults to True
        \FLAG write_sohtextfile  True  # boolean, defaults to True
        \FLAG write_sohcsvfile   True  # boolean, defaults to True


6.  In 'driving_instructions.conf' file, set FLAG 'save_starttime' to 'True' 
    so that the code 'DCL' works properly. 

    .. code-block:: text

        \FLAG save_starttime     True  # boolean, defaults to False


7.  \**** Define the actual station and its parameters. If variables 
    containing the datapaths were defined, now those can be used to shorten 
    the parameter definition.

    .. code-block:: text

        \STATION FN MSF NaN 7311537.718 592903.937 3067 PS6-24 STS-2 1970-001T12:12:00 2100-1
         \PAR 2  Data_BHZ                BHZ      1    1.0       ?         []               9    (False)                 []            []                     $Data_path
         \PAR 4  Data_coverage_day_BHZ   BHZ.DCD  1    1.0       %         [-10,110]        1    (X<95.0)                [0,100]       [95.0,NaN,90.0]        $Data_path
         \PAR 4  Data_realtimeness_BHZ   BHZ.DCL  1    1.0       %         [-10,110]        1    (X<90.0)                [0,100]       [90.0,NaN]             $Data_path
         \PAR 4  Timestamp_error_BHZ     BHZ.TSE  1    1.0       s         []               4    (X<-86400|X>86400)      []            []                     $Data_path
         \PAR 3  Timing_quality_BHZ      BHZ.TQ   9    1.0       %         [-10,110]        2    (X<90.0)                [0,100]       [95.0,NaN,90.0]        $Data_path
         \PAR 1  Longitude               LOG.long 1    1.0       °         []               2    (X<1.0)                 [20,34]       []                     $ED_log_path
         \PAR 1  Latitude                LOG.lat  1    1.0       °         []               2    (X<1.0)                 [34,73]       []                     $ED_log_path
         \PAR 1  Timing_error            AEP      60   1.0       μs        [-7.0,6.0]       2    (X<-6.0|X>5.0)          [-50,50]      [5.0,-6.0]             $Data_path
         \PAR 1  Digitizer_input_voltage AE1      60   1.0       V         [10.0,15.0]      1    (X<12.0)                [-1,20]       [13.2,NaN,12.0]        $Data_path
         \PAR 1  Digitizer_input_current AE2      60   0.001     A         [-0.1,0.5]       4    (X<0.05|X>0.4)          [-1,10]       [0.4,0.05]             $Data_path
         \PAR 1  Digitizer_temperature   AE3      60   1.0       °C        [-20.0,50.0]     4    (X<5.0|X>40.0)          [-100,100]    [40.0,5.0]             $Data_path
         \PAR 1  Offset_U                AE5      60   1.0       V         [-4.0,4.0]       3    (X<-1.5|X>1.5)          [-10,10]      [1.5,-1.5]             $Data_path
         \PAR 1  Offset_W                AE6      60   1.0       V         [-4.0,4.0]       3    (X<-1.5|X>1.5)          [-10,10]      [1.5,-1.5]             $Data_path
         \PAR 1  Offset_V                AE7      60   1.0       V         [-4.0,4.0]       3    (X<-1.5|X>1.5)          [-10,10]      [1.5,-1.5]             $Data_path
        \END


8.  \**** Call function 'process_logs' with the new station.

    .. code-block:: text
    
        \START
        
        ...
        
        \RUN process_logs FN MSF &TODAY &TODAY [1,3,4]

        ...

        \STOP

    The above line calls 'process_logs' function for 
    station with network "FN" and name "MSF". Timespan is from current
    date to current date, i.e. 1 day. Parameters with class equals 1
    are included. The line should be placed between
    START and STOP commands in the configiration file.

    The START command should be used before RUN command if any features 
    requiring the program start time information are used, e.g. codes 'DCD', 
    'DCL' and 'TSE'.


At this point the back-end for the new station should be configured.



9.  In 'conf/front/networks/FN_config.yml' file check the
    filepath formats in 'filepathformats' dictionary entry.

    .. code-block:: yaml

        filepathformats:
          stf: "~polyfemos/data_out/FN/sohtextfiles/&YEAR/&NETWORK/&STATION/&NETWORK.&STATION.&YEAR.&JULDAY"
          csv: "~polyfemos/data_out/FN/sohcsvs/&YEAR/&NETWORK/&STATION/&PARNAME/&NETWORK.&STATION.&PARNAME.&YEAR"
          alert: "~polyfemos/data_out/FN/&YEAR/&NETWORK/&STATION/&NETWORK.&STATION.&YEAR.&JULDAY"
          rawdata: "/path/to/raw/data/&YEAR/&NETWORK/&STATION/&CHANNEL.D/&NETWORK.&STATION.*.&CHANNEL.D.&YEAR.&JULDAY"


10. \**** Add station id to the list in 'station_ids' entry in file
    'conf/front/networks/FN_config.yml'. In this case the id is "FN.MSF".


11. If the station has channels or state of health parameters that none of the
    previously included stations had, add those in 'channel_codes' and
    'sohpars' entries in 'conf/front/networks/FN_config.yml'.


12. If the station's network code is not in the list of network codes (entry
    'network_codes') in 'conf/front/global_config.yml', add it.



At this point frontend should be configured, but if the station definition
introduced some other changes to frontend, define those in files
'conf/front/global_config.yml' and 'conf/front/networks/FN_config.yml'
respectively.







