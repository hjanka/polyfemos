# -*- coding: utf-8 -*-
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
Provides config values from YAML files

See more info in :ref:`FrontendConfiguration`

:copyright:
    2019, University of Oulu, Sodankyla Geophysical Observatory
:license:
    GNU Lesser General Public License v3.0 or later
    (https://spdx.org/licenses/LGPL-3.0-or-later.html)
"""
import os
import functools

from polyfemos.parser import typeoperator as to
from polyfemos.util.messenger import messenger
from polyfemos.util.randomizer import generate_secret_key
from polyfemos.util import fileutils
from polyfemos.front import request


# TODO command line and cwd
# TODO clean up, if yaml files are not found

# get current working directory
working_dir = os.getcwd()
msg = "Working directory: {}".format(working_dir)
messenger(msg, "R")

_global_config_folder = [working_dir, "conf", "front"]
_network_config_folder = [working_dir, "conf", "front", "networks"]

fn = os.path.join(*_global_config_folder, "global_config.yml")
GLOBAL_CONFIG = fileutils.load_yaml(fn)


def users():
    """
    :rtype: dict
    :return: ``users`` dictionary from global config yaml file
    """
    if GLOBAL_CONFIG is None:
        return []
    return GLOBAL_CONFIG["users"]


def network_codes():
    """
    :rtype: list
    :return: ``network_codes`` list from global config yaml file
    """
    if GLOBAL_CONFIG is None:
        return []
    return GLOBAL_CONFIG["network_codes"]


def secret_key():
    """
    A ``secret_key`` entry is read from the global configuration yaml file.
    If no secret key is given in the configuration file or the default
    entry is unchanged, a different random secret key is used
    when polyfemos web is reloaded.

    See :func:`~polyfemos.util.randomizer.generate_secret_key`
    for more info.

    :rtype: str
    :return: secret key
    """
    if GLOBAL_CONFIG is None:
        return generate_secret_key()
    sk = GLOBAL_CONFIG["secret_key"]
    if not sk or sk is None or sk.lower() in "changethisimmediately!":
        sk = generate_secret_key()
    return sk


if GLOBAL_CONFIG is not None:
    NETWORK_CONFIG = {}
    for network_code in network_codes():
        fn = os.path.join(
            *_network_config_folder, "{}_config.yml".format(network_code))
        _network_config = fileutils.load_yaml(fn)
        if _network_config is not None:
            NETWORK_CONFIG[network_code] = _network_config
            NETWORK_CONFIG[network_code]["paths"] \
                .update(GLOBAL_CONFIG["paths"])


def get_network_code():
    """
    Fetches the code of the currently selected network from cookies.
    If none is selected returns the default network code, which is the
    first entry in the ``network_codes`` list in ``global_config.yml`` file.

    :rtype: str
    :return: network code
    """
    try:
        network_code = request.cookie("network_code")
    except RuntimeError:
        network_code = None
    if network_code in request.nones():
        network_code = ""
        ncs = network_codes()
        if len(ncs) > 0:
            network_code = ncs[0]
    return network_code


def check_network_code(func_):
    """
    Decorated functions check for currently selected network code.
    The name of the decorated function is used to extract the configuration
    value from the networks configuration yaml file. If the value
    is present in the configuration file it is passed to the ``func_``
    as ``config_value`` keyword argument.

    :type func\_: func
    :param func\_:
    :rtype: func
    :return: a decorated function
    """
    @functools.wraps(func_)
    def wrapper(*args, **kwargs):
        network_code = get_network_code()
        try:
            config_value = NETWORK_CONFIG[network_code][func_.__name__]
        except (KeyError, NameError):
            # Catch NameError if NETWORK_CONFIG is not defined
            return func_(*args, **kwargs)
        kwargs["config_value"] = config_value
        return func_(*args, **kwargs)
    return wrapper


@check_network_code
def paths(key, config_value={}):
    """
    :type key: str
    :param key: The desired filepath from the ``paths`` dictionary
    :type config_value: dict
    :param config_value: ``paths`` dictionary from yaml files
    :rtype: str
    :return:
    """
    path = config_value.get(key, "")
    return to.staticfilepath(path)


@check_network_code
def filepathformats(key, config_value={}):
    """
    :type key: str
    :param key: The desired filepathformat from the
        ``filepathformats`` dictionary
    :type config_value: dict
    :param config_value: ``filepathformats`` dictionary from yaml files
    :rtype: func
    :return:
    """
    path = config_value.get(key, "")
    return to.filepath(path)


@check_network_code
def sohpars(visibilities={1, 2}, config_value=[]):
    """
    :type visibilities: set
    :param visibilities: returned sohpars are selected based on given
        visibilities
    :type config_value: list
    :param config_value: list of state of health parameter
        dictionaries from yaml files
    :rtype: list[str]
    :return: list of state of health parameter names
    """
    return [s["name"] for s in config_value if s["visibility"] in visibilities]


@check_network_code
def station_ids(config_value=[]):
    """
    :type config_value: list
    :param config_value: ``station_ids`` from yaml files
    :rtype: list[str]
    :return: list of station ids (e.g. ``"FN.MSF"``) visible in polyfemos web
    """
    return config_value


@check_network_code
def channel_codes(config_value=[]):
    """
    :type config_value: list
    :param config_value: ``channel_codes`` from yaml files
    :rtype: list[str]
    :return: list of all data channels available in polyfemos web across
        all the stations in the selected network
    """
    return config_value


_js_template = """
dict = {{
{}
}}
if (tick in dict) {{
    return dict[tick]
}}
else {{
    return ""
}}
"""


@check_network_code
def ticklabels(key, config_value={}):
    """
    If some state of health parameters require specific
    Y axis labeling, the custom tick labels are defined here.

    keys of the 'tl' dictionary are names of the soh parameters.
    Values are JavaScript code blocks which define the tick labels.
    Word 'tick' in JS code will be interpreted as tick variable.

    :type key: str
    :param key: Name of the soh parameter
    :type config_value: dict
    :param config_value: ``ticklabels`` dictionary from yaml files
    :rtype: str
    :return: JavaScript code mapping the integer data values into
        string values.
    """
    if key not in config_value:
        return False

    dict_str = ""
    for k, v in config_value[key].items():
        dict_str += "    {}: \"{}\",\n".format(k, v)

    return _js_template.format(dict_str)


@check_network_code
def definitions(key, config_value={}):
    """
    :type key: str
    :param key: internal name for definition, e.g. 'datarealtimeness'
    :type config_value: dict
    :param config_value: a dictionary from yaml files mapping
        the internal names in to their user defined values
    :rtype: str
    :return: user defined value corresponding the internal name
    """
    return config_value.get(key, "")


@check_network_code
def summary_outlierremfunc_info(config_value=[]):
    """
    :type config_value: list
    :param config_value:
    :rtype: list[str]
    :return: For summary table page, information about used
        advanced outlier removal options
    """
    return config_value


def get_outlierremfunc(function="", **kwargs):
    """
    Available functions:

    - lipschitz, :func:`~polyfemos.data.outlierremover.lipschitz`
    - stalta, :func:`~polyfemos.data.outlierremover.stalta`
    - dtr, :func:`~polyfemos.data.outlierremover.dtr`

    :type function: str
    :param function:
    :rtype: func
    :return: outlier removal function with additional ``kwargs``
        applied to it.
        If an invalid ``function`` is given, returns ``False``
    """
    from polyfemos.data import outlierremover
    # Available outlier removal functions
    funcs = {
        "lipschitz": outlierremover.lipschitz,
        "stalta": outlierremover.stalta,
        "dtr": outlierremover.dtr,
    }
    if function not in funcs:
        return False
    return lambda data: funcs[function](data, **kwargs)


@check_network_code
def summary_outlierremfuncs(station_id="", sohpar_name="", config_value={}):
    """
    :type station_id: str
    :param station_id: id of the station, e.g. "FN.MSF"
    :type sohpar_name: str
    :param sohpar_name: name of the state of health parameter
    :type config_value: dict
    :param config_value: the ``summary_outlierremfuncs`` dictionary
        from yaml files
    :rtype: func
    :return: outlier removal function corresponding ``station_id`` and
        ``sohpar_name`` pair. User may define different outlier removal
        functions with different ``station_id`` and ``sohpar_name``
        combinations. The key in the dict should be
        ``station_id:sohpar_name``, e.g. ``FN.RANF:Vault_temperature``.
    """
    key = "{}:{}".format(station_id, sohpar_name)
    if key not in config_value:
        return False
    return get_outlierremfunc(**config_value[key])


def get_datacoveragebrowser_func(function="", **kwargs):
    """
    Available functions:

    - seismic_scanner,
        :func:`~polyfemos.back.seismic.scanner.get_data_coverage_figure`

    :type function: str
    :param function:
    :rtype: func
    :return: data coverage scanner function.
        If an invalid ``function`` is given, returns ``False``.
    """
    from polyfemos.back.seismic.scanner import (get_data_coverage_figure,
                                                null_figure)
    # Available scanner functions
    funcs = {
        "seismic_scanner": get_data_coverage_figure,
        "null_scanner": null_figure,
    }
    if function not in funcs:
        return False
    return funcs[function]


@check_network_code
def datacoveragebrowser_func(config_value=""):
    """
    :type config_value: str
    :param config_value: ``datacoveragebrowser_func`` value from
        yaml files
    :rtype: func
    :return: see :func:`~polyfemos.front.userdef.get_datacoveragebrowser_func`
        for more info.
    """
    return get_datacoveragebrowser_func(function=config_value)


def transform_func(key):
    """
    :type key: str
    :param key: internal sensor code
    :rtype: func
    :return: UWV to NEZ transform function
    """
    from math import sqrt

    def func1(u, w, v):
        # for streckeisen
        x = -1. * u * sqrt(2. / 3.) + (v + w) / sqrt(6.)
        y = (v - w) / sqrt(2.)
        z = (u + v + w) / sqrt(3.)
        return (x, y, z)

    def func2(u, w, v):
        # for nanometrics
        x = (2. * u - v - w) / sqrt(6.)
        y = (v - w) / sqrt(2.)
        z = (u + v + w) / sqrt(3.)
        return (x, y, z)

    funcs = {
        "STS-2": func1,
        "Trillium_120PH": func2,
        "Trillium_120PA": func2,
        "Trillium_Co120": func2,
    }

    if key not in funcs:
        msg = "Invalid key in transform_func"
        messenger(msg, "W")
        return lambda x, y, z: (x, y, z)

    return funcs[key]


if __name__ == "__main__":

    print("Ticklabels")
    print(ticklabels("GPS_status"))
    print(ticklabels("GPS_status_asd"))

    print("\nPaths")
    print(paths("server_ip"))
    print(paths("server_ip_asd"))

    print("\nStation IDs")
    print(station_ids())

    print("\nChannel Codes")
    print(channel_codes())

    print("\nSohpars")
    print(sohpars(visibilities={2}))

    print("\nDefinitions")
    print(definitions("datarealtimeness"))

    print("\nFPFs")
    print(filepathformats("stf"))

    print("\nOutlier removal")
    print(summary_outlierremfunc_info())

    print(summary_outlierremfuncs(
        station_id="FN.RANF", sohpar_name="Vault_temperature"))
    print(summary_outlierremfuncs("asd", "asd"))

    print(datacoveragebrowser_func())
