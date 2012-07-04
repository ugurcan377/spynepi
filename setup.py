#!/usr/bin/env python

import os
import re

from setuptools import setup
from setuptools import find_packages

PROJECT_NAME = 'spynepi'

v = open(os.path.join(os.path.dirname(__file__), PROJECT_NAME, '__init__.py'), 'r')
VERSION = re.match(r".*__version__ = '(.*?)'", v.read(), re.S).group(1)

setup(
    name=PROJECT_NAME,
    packages=find_packages(),
    version=VERSION,
    author='Ugurcan Ergun',
    author_email='ugurcanergn@gmail.com',
    url='http://github.com/ugurcan377/spynepi',
    license='GPL',
    install_requires=[
      #'lxml>=2.2.1',
    ],

    entry_points = {
        'console_scripts': [
            '%(p)s=%(p)s.main:main' % {'p': PROJECT_NAME},
        ]
    },
)
