#!/usr/bin/env python
# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- encoding: utf-8 -*-

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext
from setuptools import setup, find_packages

setup(
    name='tldist',
    version='0.1dev',
    license='BSD',
    description='Pytest plugin for detecting inadvertent open file handles',
    long_description='Transfer Learning API',
    author='Craig Jones',
    author_email='astropy.team@gmail.com',
    url='https://astropy.org',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
    ],
    keywords=[ 'detect', 'open', 'file', 'handle', 'psutil', 'pytest', 'py.test' ],
    install_requires=[ 'pytest>=2.8.0', 'psutil' ],
    python_requires='>=3.5'
)
