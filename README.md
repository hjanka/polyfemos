# README #


### polyfemos ###

A Python package for observatory realtime state of health monitoring.
Includes 


### Short setup guide ###

Before installation make sure you have Python 3.7 together with Anaconda and
pip installed.

Extract this compressed package for example into your home folder
so that the end result is

- ~/polyfemos/setup1.sh
- ~/polyfemos/setup2.sh
- ...

Do not touch the polyfemos tar file with version number included.
It is the polyfemos python package and will be installed using pip in step 2.

If you don't want to setup polyfemos production web server with uwsgi and
nginx you may skip step 3.

1. Go to the folder with setup scripts in it. If you followed the above
instructions, the correct folder is found using command `cd ~/polyfemos`.

2. Run `bash setup1.sh` as the user which will become
the host for polyfemos, no sudo privileges needed.

3. Run `sudo bash setup2.sh` as user with sudo privileges
(same or different user as in the step 2.)

When updating polyfemos package these setup scripts are not needed.
Just upgrade polyfemos package for example by using command
`python -m pip install path/to/polyfemos-*.tar.gz`
while 'polyfemos_env' conda environment is activated.

If you've set up the production server, run command
`sudo systemctl restart polyfemos_web.service`
to apply the changes.

Polyfemos comes with a bunch of command line scripts. For example:

- `polyfemos-tfp`, to test the web server side paths defined in YAML files.
- `polyfemos-devserver`, to launch flask development server.
- `polyfemos-readconf`, to read backend `*.conf` files


### Contributors ###

- Jänkävaara, Henrik
- Narkilahti, Janne
- Ulich, Thomas


### Contact ###

polyfemos.dev@gmail.com



