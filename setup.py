#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import dj_timetravel_postgres

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = dj_timetravel_postgres.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='dj-timetravel-postgres',
    version=version,
    description='Full featured audit functionality for Django with Postgres',
    long_description=readme + '\n\n' + history,
    author='Richard Bann',
    author_email='richard.bann@vertis.com',
    url='https://github.com/vertisfinance/dj-timetravel-postgres',
    packages=[
        'dj_timetravel_postgres',
    ],
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='dj-timetravel-postgres',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
