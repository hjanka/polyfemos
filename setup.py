#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Polyfemos - A State of Health monitoring package for observatories.
"""
# This file is part of Polyfemos.

# Polyfemos is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or any later version.

# Polyfemos is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.

# You should have received a copy of the GNU Lesser General Public License and
# GNU General Public License along with Polyfemos. If not, see
# <https://www.gnu.org/licenses/>.

# :author:
#     Henrik Jänkävaara,
# :copyright:
#     2019, University of Oulu,
#     Sodankyla Geophysical Observatory
# :license:
#     GNU Lesser General Public License v3.0 or later
#     (https://spdx.org/licenses/LGPL-3.0-or-later.html)

import os

from setuptools import setup, find_packages


version = "0.0.0"
vfile = os.path.join("polyfemos", "VERSION.txt")
if os.path.isfile(vfile):
    with open(vfile) as f:
        version = f.readline().strip()
print("polyfemos version:", version)


INSTALL_REQUIRES = [
    "numpy>=1.16.4",
    "obspy>=1.1.1",
    "pathos>=0.2.3",
    "scikit-learn>=0.21.2",
    "bokeh>=1.0.2",
    "flask>=1.0.2",
    "flask_wtf",
]
KEYWORDS = [
    "MiniSEED", "MSEED", "observatory", "real time", "realtime", "seismology",
    "signal", "state of health", "housekeeping",
]
ENTRY_POINTS = {
    'console_scripts': [
        'polyfemos-devserver = polyfemos.scripts.devserver:main',
        'polyfemos-readconf = polyfemos.back.main:readconf',
        'polyfemos-tfp = polyfemos.scripts.test_front_paths:main',
        'polyfemos-rwt = polyfemos.scripts.render_web_templates:main',
        'polyfemos-secret_key = polyfemos.util.randomizer:get_secret_key',
        'polyfemos-sohemailer = polyfemos.scripts.sohemailer:main',
        'polyfemos-check = polyfemos.scripts.check_output_files:main',
    ],
}


def setup_package():
    setup(
        name='polyfemos',
        version=version,
        description='Observatory State of Health monitoring package',
        long_description='',
        url='https://bitbucket.org/hjanka/polyfemos_source/src/master/',
        author='HJ',
        author_email='polyfemos.dev@gmail.com',
        license='GNU Lesser General Public License v3 or later (LGPLv3+)',
        platforms='Ubuntu 16.04',
        keywords=KEYWORDS,
        entry_points=ENTRY_POINTS,
        classifiers=[
            # 'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Science/Research',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.7',
            'Topic :: Scientific/Engineering',
        ],
        packages=find_packages(exclude=['.git*']),
        install_requires=INSTALL_REQUIRES,
        include_package_data=True,
        zip_safe=False,
    )


if __name__ == '__main__':
    setup_package()
