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



Setup
=====


This is a short tutorial describing the steps to install Polyfemos.
SUDO privileges are needed.
User 'sysop' will refer to the user (not sudo) hosting the polyfemos.
User 'admin' will refer to the user with sudo privileges.



I General
---------

1.  Install 'Anaconda' (e.g. Anaconda3) and PIP if you haven't already.

2.  Extract the compressed file in which everything is contained. 
    Suggested location is your home folder, so that the end result is as 
    follows: '/home/sysop/polyfemos'

3.  If wanted, move 'data_out' and 'logs' folders their preferred 
    locations, or create additional folders (named for example 
    'polyfemos_logs' and 'polyfemos_data_out') somewhere in your computer.

4.  Go to folder '/home/sysop/polyfemos'

5.  Run 'setup1.sh' script to install all necessary packages.
    The user you are currently logged in as, will became the host of polyfemos.
    The script assumes you have anaconda installed. No need for sudo privileges.



II Backend
----------

1.  Check all '\*.conf' files and wrapper scripts in 'conf/back' folder 

    -   All settings of the backend are defined in '\*.conf' files.
        By default there are three '\*.conf' files: 'driving_instructions.conf',
        'folders.conf' and 'stations.conf'. For more about '\*.conf' files
        in chapter :ref:`ConfigurationFiles`.
    -   The program is advised to be called using bash wrapper file.
        The default file is 'wrapper.sh'

2.  Setup crontab. An example line running the backend script every minute:

    ``* * * * * /home/sysop/polyfemos/conf/back/FN/wrapper.sh >/dev/null 2>&1``



III Fontend
-----------

1.  If your user does not have sudo privileges, change your user to user with 
    sudo privileges. Make sure you are in folder '/home/sysop/polyfemos'.
    (Note that the home folder is the home of the host of polyfemos, not 
    admin's, if the users differ that is.

2.  Check that filepaths in file 'conf/front/global_config.yml' exists.
    Most importantly fields 'nginx_dir', 'env_dir', and 'service_dir' should 
    have correct file paths at this point.
    The field 'passwd_file' will be the used password file and 
    if it doesn't exist it will be created during the setup.

3.  Run script 'setup2.sh', some commands in the script ask for sudo
    privileges. 



Uninstall
---------

Polyfemos comes with additional uninstall script 'uninstall.sh', which may be
used to uninstall nginx, apache2-utils and to remove polyfemos_env conda
environment and it's unused dependencies. Additionally, the uninstall script
removes files created during setup, but leaves the folder
'/home/sysop/polyfemos' otherwise untouched. In addition, the script doesn't
remove output data files or log files.

If you used setup scripts 'setup1.sh' and 'setup2.sh' for installing
polyfemos, additional information about the setup is found in files: 
'polyfemos_installed_files.txt' and 'polyfemos_setup_log.txt'.






