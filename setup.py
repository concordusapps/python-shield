#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from pkgutil import get_importer
from os import path

# Calculate the base directory of the project.
BASE_DIR = path.abspath(path.dirname(__file__))

# Navigate, import, and retrieve the version of the project.
VERSION = get_importer(path.join(BASE_DIR, 'src', 'shield')).find_module(
    'meta').load_module('meta').version

setup(
    name='shield',
    version=VERSION,
    description='A permissions framework built around declarative rules.',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3'
    ],
    license='MIT',
    author='Concordus Applications',
    author_email='support@concordusapps.com',
    url='http://github.com/concordusapps/python-shield',
    package_dir={'shield': 'src/shield'},
    packages=find_packages(path.join(BASE_DIR, 'src')),
    install_requires=(
        # Normalization between python 2.x and 3.x
        'six'
    ),
    extras_require={
        'test': (
            # Test runner.
            'pytest',

            # Ensure PEP8 conformance.
            'pytest-pep8',

            # Ensure test coverage.
            'pytest-cov',

            # SQLAlchemy is the Python SQL toolkit and Object Relational Mapper
            # that gives application developers the full power and flexibility
            # of SQL.
            'sqlalchemy'
        )
    }
)
