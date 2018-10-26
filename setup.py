#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

dynamic_requires = []

setup(
    name='antsar-avion',
    version='0.9.1',
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
        'bluepy>==1.1.4',
        'csrmesh>=0.9.0',
        'requests>=2.18.4',
    ],
    include_package_data=True,
    zip_safe=False,
)
