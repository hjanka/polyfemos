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

cat licence_notice_short.txt 
echo ""

echo "Continue to uninstall polyfemos? [Y/n]"
poll_exit

for file in $(cat polyfemos_installed_files.txt); do
    echo "Removing file $file"
    sudo rm "$file"
done


echo "Remove 'polyfemos_env' conda environment and dependencies? [Y/n]"
read -p "" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    source deactivate
    conda remove -n polyfemos_env --all
    conda clean -p
fi


echo "Remove 'apache2-utils' and dependencies? [Y/n]"
read -p "" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo apt-get remove apache2-utils
    sudo apt-get autoremove
fi


echo "Remove 'nginx', it's dependencies and config files? [Y/n]"
read -p "" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo apt-get purge nginx nginx-common
    sudo apt-get autoremove
fi


echo "Uninstall completed."
echo "The contents in this folder"
echo "($pwd)",
echo "output files and logs are not deleted."

