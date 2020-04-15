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
Test polyfemos frontend paths

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import os

from argparse import ArgumentParser

from polyfemos.parser import typeoperator as to
from polyfemos.parser import resources
from polyfemos.util import fileutils


_funcs = {
    "file": os.path.isfile,
    "dir": os.path.isdir,
}


def check_paths(paths, key, priority, ford):
    """
    :type paths: dict
    :param paths: dictionary containing paths
    :type key: str
    :param key:
    :type priority: str
    :param priority:
    :type ford: str
    :param ford: "file" or "dir"
    """
    warning = False
    func = _funcs[ford]
    msg = key
    fn = ""
    if key not in paths:
        msg += " - No path '{}' defined.".format(key)
        warning |= True
    else:
        fn = to.staticfilepath(paths[key])
    msg += " - {} {}".format(ford, fn)
    if func(fn):
        msg += " exists.".format(fn)
    else:
        msg += " does not exist."
        warning |= True
    if warning:
        msg += " - Warning, priority: {}".format(priority)
    print(msg)


_global_paths = [
    ["working_dir", "HIGH", "dir"],
    ["nginx_dir", "HIGH", "dir"],
    ["env_dir", "HIGH", "dir"],
    ["service_dir", "HIGH", "dir"],
    ["passwd_file", "HIGH", "file"],
    ["webusagelog_file", "MED", "file"],
    ["nginx_log_dir", "MED", "dir"],
    ["uwsgi_log_dir", "MED", "dir"],
    ["ttf_file", "LOW", "file"],
    ["doc_dir", "LOW", "dir"],
]
_network_paths = [
    # paths
    ["dci_file", "LOW", "file"],
    ["map_file", "LOW", "file"],
    # filepathformats
    ["stf", "LOW", "dir"],
    ["csv", "LOW", "dir"],
    ["alert", "LOW", "dir"],
    ["rawdata", "LOW", "dir"],
]
_network_fpfs = [
]


def main(argv=None):
    """
    Recursively checks folders for YAML files for defined paths.

    :type argv: list
    :param argv: command line arguments
    """
    parser = ArgumentParser(prog='polyfemos-tfp',
                            description=__doc__.strip())
    parser.add_argument('path', type=str,
                        help='YAML file or directory containing YAML files.')
    parser.add_argument('-w', '--wanted', type=str, default="",
                        help='Specific path to be requested from YAML files.')
    args = parser.parse_args(argv)

    path = args.path
    wanted_path = args.wanted

    if os.path.isdir(path) or os.path.isfile(path):
        pass
    else:
        msg = "The given file/directory does not exist."
        print(msg)
        return

    if os.path.isfile(path) and path.endswith((".yml", ".yaml")):
        fns = [path]
    else:
        fns = []
        for dirname, _, filenames in os.walk(path):
            for filename in filenames:
                if filename.endswith((".yml", ".yaml")):
                    fns.append(os.path.join(dirname, filename))

    for fn in fns:
        if not wanted_path:
            print("\n{}:\n".format(fn))
        yamlfile = fileutils.load_yaml(fn, quiet=True)
        if yamlfile is None:
            continue
        _paths = _global_paths
        if "networks" in fn:
            _paths = _network_paths
        dict_ = {}
        if "paths" in yamlfile:
            if wanted_path in yamlfile["paths"]:
                print(to.staticfilepath(yamlfile["paths"][wanted_path]))
                return
            elif wanted_path:
                continue
            dict_.update(yamlfile["paths"])
        if "filepathformats" in yamlfile:
            fpfs = yamlfile["filepathformats"]
            func_ = lambda x: x.split(resources.SYMBOLS["RESVAR"])[0]
            fpfs = {k: func_(v) for k, v in fpfs.items()}
            dict_.update(fpfs)
        print()
        for args in _paths:
            check_paths(dict_, *args)


if __name__ == "__main__":
    main()
