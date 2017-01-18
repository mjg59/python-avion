#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from setuptools import setup, find_packages
import sys
import warnings

dynamic_requires = []

version = 0.4

setup(
    name='avion',
    version=0.4,
    author='Matthew Garrett',
    author_email='mjg59@srcf.ucam.org',
    url='http://github.com/mjg59/python-avion',
    packages=find_packages(),
    scripts=[],
    description='Python API for controlling Avi-on Bluetooth dimmers',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=[
        'bluepy',
        'csrmesh',
    ],
    include_package_data=True,
    zip_safe=False,
)
