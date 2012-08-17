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
    description="This is a caching PyPI implementation that uses spyne",
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Intended Audience :: Developers',
    ],
    keywords=('pypi', 'spyne', 'wsgi', 'rpc', 'http'),
    author='Ugurcan Ergun',
    author_email='ugurcanergn@gmail.com',
    url='http://github.com/ugurcan377/spynepi',
    license='GPL',

    install_requires=[
        "spyne<3.0", "sqlalchemy<0.8", "werkzeug", "twisted",
    ],
    include_package_data=True,
    entry_points = {
        'console_scripts': [
            '%(p)s_daemon=%(p)s.main:main' % {'p': PROJECT_NAME},
        ]
    },
)
