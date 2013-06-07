#! /usr/bin/env python
import os
from setuptools import setup, find_packages


setup(
    name='python-shield',
    version='0.6.0',
    description='An object-level permissions backend for django/sqlalchemy using expressive rules.',
    license='MIT',
    author='Concordus Applications',
    author_email='support@concordusapps.com',
    url='https://github.com/CactusCommander/python-shield',
    package_dir={'shield': 'src/shield'},
    packages=find_packages('src'),
    install_requires=[
        'django >= 1.5',
        'six >= 1.3'
    ],
)
