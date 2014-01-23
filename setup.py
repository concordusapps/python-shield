#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from imp import load_source


setup(
    name='shield',
    version=load_source('', 'shield/_version.py').__version__,
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
    packages=find_packages('.'),
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

            # The Web framework for perfectionists with deadlines.
            'django',

            # SQLAlchemy is the Python SQL toolkit and Object Relational Mapper
            # that gives application developers the full power and flexibility
            # of SQL.
            'sqlalchemy'
        )
    }
)
