#!/bin/bash

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

log_installed () {
    echo -e $1 >> "polyfemos_installed_files.txt"
}
log_setup () {
    echo -e $1 >> "polyfemos_setup_log.txt"
}

cat licence_notice_short.txt 
echo ""

echo "The user executing this setup script must have sudo privileges."
echo "NGINX will also be installed, use option '--no-nginx'"
echo "to skip the installation of NGINX"
echo "Use '--no-passwd' option if you don't want to configure passwords"
echo "Continue?"
poll_exit


location_of_python_executable=$(cat ".location_of_python_executable.txt") 
python_directory=$(dirname $location_of_python_executable)
export PATH="$python_directory:$PATH"
alias python=$location_of_python_executable
echo $PATH
echo $location_of_python_executable


log_setup "\n"
log_installed "\n"


if [[ "$@" =~ "--no-nginx" ]]; then
    :
else
    echo -e "\nInstalling NGINX"
    sudo apt-get install nginx
    nginx -v
    log_setup "nginx installed"
fi

printf "\nPython import check"
import_error=$(python -c \
"
try:
    import jinja2
    import yaml
except ImportError as e:
    print(e)
")
if [[ $import_error ]]; then
    echo
    echo $import_error
    echo "Exiting"
    exit 1
else
    printf " - OK!\n"
fi


echo "Setting-up polyfemos_web"
echo "In folder:"
pwd
sleep 1
echo "Script location:"
echo $0
sleep 1

script_folder=$(dirname $0)
if [[ $script_folder != "." ]]; then
    echo "The setup_web script should be called from the location of the script."
    echo "The path to file 'conf/front/global_config.yml' should be available"
    echo "in the folder where the setup script is located."
    echo "Exiting"
    exit 1
fi


echo -e "\nNext up, the setup will create and distribute"
echo "files needed to run polyfemos on nginx server."
echo "Continue setting up polyfemos_web?"
poll_exit


if [[ "$@" =~ "--no-passwd" ]]; then
    :
else
    echo -e "\nCreating user/password for restricted parts of polyfemos"
    passwd_file=$(polyfemos-tfp conf/front/global_config.yml -w passwd_file)
    sudo apt-get install apache2-utils
    log_setup "apache2-utils installed"
    sudo touch $passwd_file
    log_installed "$passwd_file"
    echo -e "\nGive username for restricted parts of polyfemos"
    read username
    sudo htpasswd $passwd_file $username
fi


echo -e "\nChecking paths in 'conf/front/global_config.yml'"
filepath_check_result=$(polyfemos-tfp conf/front/global_config.yml)
missing_files=$(echo "$filepath_check_result" | grep "Warning")
if [[ $missing_files ]]; then
    echo "The following files and/or folders are not found:"
    echo "$missing_files"
    echo "Continue anyway? [Y/n]"
    poll_exit
fi


sudo chmod a+rx *
sudo rm -rf .temp >/dev/null


echo -e "\nRendering and distributing templates"

working_dir=$(polyfemos-tfp conf/front/global_config.yml -w working_dir)
nginx_dir=$(polyfemos-tfp conf/front/global_config.yml -w nginx_dir)
service_dir=$(polyfemos-tfp conf/front/global_config.yml -w service_dir)

echo "working_dir   $working_dir"
echo "nginx_dir     $nginx_dir"
echo "service_dir   $service_dir"


echo \
"# -*- coding: utf-8 -*-
from polyfemos.front.main import app
if __name__ == \"__main__\":
    app.run()" > $working_dir/wsgi.py
chmod 777 $working_dir/wsgi.py
chown www-data:www-data $working_dir/wsgi.py
log_installed "$working_dir/wsgi.py"


chmod a+w $working_dir
chmod a+rx $working_dir/*

sudo chmod a+w $nginx_dir/sites-available

rm -f $working_dir/polyfemos_web.ini
rm -f $working_dir/polyfemos_web.sock
rm -f $nginx_dir/sites-available/polyfemos*

sudo rm -f $nginx_dir/sites-enabled/polyfemos*
sudo rm -f $service_dir/polyfemos_web.service


mkdir .temp >/dev/null
mkdir .temp/nginx >/dev/null
chmod -R a+rw .temp


# Create files from web setup templates
polyfemos-rwt conf/front/global_config.yml
chmod -R a+rw .temp


mv .temp/nginx/polyfemos* $nginx_dir/sites-available
log_installed "$nginx_dir/sites-available/polyfemos*"
mv .temp/polyfemos_web.ini $working_dir
log_installed "$working_dir/polyfemos_web.ini"
sudo mv .temp/polyfemos_web.service $service_dir
log_installed "$service_dir/polyfemos_web.service"

rm -rf .temp >/dev/null

chown -R www-data:www-data $working_dir/polyfemos_web.ini
chmod 755 $working_dir/polyfemos_web.ini

sudo chown -R www-data:www-data $nginx_dir/sites-available/polyfemos*
sudo chmod 777 $nginx_dir/sites-available/polyfemos*

sudo chown -R www-data:www-data $service_dir/polyfemos_web.service
sudo chmod 664 $service_dir/polyfemos_web.service

touch $working_dir/polyfemos_web.sock
log_installed "$working_dir/polyfemos_web.sock"
chmod 777 $working_dir/polyfemos_web.sock
chown -R www-data:www-data $working_dir/polyfemos_web.sock

touch $working_dir/.ipstorage.txt
log_installed "$working_dir/.ipstorage.txt"
chmod 777 $working_dir/.ipstorage.txt
chown -R www-data:www-data $working_dir/.ipstorage.txt




echo -e "\nSetting-up UWSGI"
echo "Killing uWSGI processes"
sudo pkill -f uwsgi -9 >/dev/null


echo -e "\nTesting uWSGI, timeout 5 seconds"
cd $working_dir
timeout 5 \
    uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi:app --enable-threads


# start now
echo "systemctl start polyfemos_web"
sudo systemctl start polyfemos_web
# start on boot
echo "systemctl enable polyfemos_web"
sudo systemctl enable polyfemos_web
echo "systemctl daemon-reload"
sudo systemctl daemon-reload


echo -e "\nSetting-up NGINX"
# create link
sudo ln -s $nginx_dir/sites-available/polyfemos_web $nginx_dir/sites-enabled
log_installed "$nginx_dir/sites-enabled/polyfemos*"
# check for errors
sudo nginx -t
# restart
sudo systemctl restart nginx


echo -e "\nAllowing NGINX through firewall"
sudo ufw allow 'Nginx Full'
log_setup "ufw, nginx allowed through firewall"


timeout 5 sudo systemctl restart polyfemos_web.service

