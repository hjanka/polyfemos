#!/bin/bash

# The setup will quide you through polyfemos install
# 1. Run 'setup1.sh' as the user which will become
# the host for polyfemos, no sudo privileges needed.
# 2. Run 'setup2.sh' as user with sudo privileges
# (same or different user as in the step 1.)

# After successful install
# debugging in polyfemos_env environment and web server run
# 'polyfemos-devserver' command
# to start flask dev server
# Command 'polyfemos-readconf' may be used to read and execute
# '*.conf' files read by polyfemos backend

# owner of the log files and folders might need to be set to
# sysop or www-data
# example command:
# sudo chown -R www-data:www-data /var/log/uwsgi/

poll_exit () {
    read -p "" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        true
    else
        echo "Exiting"
        exit 1
    fi
}

cat licence_notice_short.txt 
echo ""

echo "The setup requires Anaconda and pip installed."
echo "The setup will create 'polyfemos_env' conda environment,"
echo "install polyfemos package and other packages required."
echo "Continue setting up polyfemos?"
poll_exit

conda create -n polyfemos_env python=3.7
conda config --add channels conda-forge
source activate polyfemos_env
# for obspy numpy has to be installed separately
conda install numpy
python -m pip install polyfemos-*.tar.gz
# Installing the specific pyproj version using pip was problematic
# and it seemed like obspy 1.1.1 was not compatible 
# the pyproj version provided by pip.
conda install pyproj=1.9.5.1


# the location of python in polyfemos_env is saved
# for later use if the user with sudo privileges is not the
# host of polyfemos
location_of_python_executable=$(which python)
echo $location_of_python_executable > .location_of_python_executable.txt

echo -e "\nDo you want to install uwsgi?"
echo "It is needed for setting up the web server."
read -p "" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    conda install uwsgi
fi

echo -e "\nChecking NTP status (command 'timedatectl')"
timedatectl
echo "In order to polyfemos to work properly in realtime check if the"
echo "following options are set to 'yes':"
echo "' Network time on: yes'"
echo "'NTP synchronized: yes'"



