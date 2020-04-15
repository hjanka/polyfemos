#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# This file is part of Polyfemos.
#
# Polyfemos is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or any later version.
#
# Polyfemos is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License and
# GNU General Public License along with Polyfemos. If not, see
# <https://www.gnu.org/licenses/>.'
#
# Author: Henrik Jänkävaara
# -----------------------------------------------------------------------------
"""
A script to replace values in web templates with values defined in
YAML configuration files.

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import os

from argparse import ArgumentParser

from polyfemos.util import fileutils


_template_dir = os.path.join(os.path.dirname(__file__), "web_setup_templates")

_dict = {
    ".temp":
    [
        os.path.join(
            _template_dir, "polyfemos_web.service"),
        os.path.join(
            _template_dir, "polyfemos_web.ini"),
    ],
    os.path.join(".temp", "nginx"):
    [
        os.path.join(
            _template_dir, "nginx", "polyfemos_location.conf"),
        os.path.join(
            _template_dir, "nginx", "polyfemos_private_location.conf"),
        os.path.join(
            _template_dir, "nginx", "polyfemos_public_location.conf"),
        os.path.join(
            _template_dir, "nginx", "polyfemos_web"),
    ],
}


def main(argv=None):
    """
    :type argv: list
    :param argv: command line arguments
    """
    parser = ArgumentParser(prog='polyfemos-rwt',
                            description=__doc__.strip())
    parser.add_argument('yamlfile', type=str,
                        help='YAML configuration file')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Shows what the command would have done without '
                             'actually doing anything.')
    args = parser.parse_args(argv)

    yaml_config_filepath = args.yamlfile
    dry_run = args.dry_run

    if not os.path.isfile(yaml_config_filepath):
        print("The given YAML file does not exist.")
        return

    yaml_config_file = fileutils.load_yaml(yaml_config_filepath)
    if "paths" in yaml_config_file:
        paths = yaml_config_file["paths"]
    else:
        print("No 'paths' available in given YAML file.")
        return

    for to_folder, templates in _dict.items():

        if not os.path.exists(to_folder):
            print("\nCreating directory: {}".format(to_folder))
            if not dry_run:
                os.makedirs(to_folder)

        for template in templates:
            filename = os.path.basename(template)
            str_ = fileutils.render_template(template, paths)

            filepath = os.path.join(to_folder, filename)

            print("\nCreating file: {}".format(filepath))
            print("with contents:\n{}".format(str_))

            if not dry_run:
                with open(filepath, 'w') as f:
                    f.write(str_)


if __name__ == "__main__":
    main()
