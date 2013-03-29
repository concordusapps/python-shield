#! /usr/bin/env python
import os
import re
from setuptools import setup, find_packages


setup(
    name='django-shield',
    version='0.5.0',
    description='An object-level permissions backend for django using expressive rules.',
    license='MIT',
    author='Concordus Applications',
    author_email='support@concordusapps.com',
    url='http://github.com/concordusapps/django-shield/',
    package_dir={'shield': 'src/shield'},
    packages=find_packages('src'),
    install_requires=[
        'django >= 1.5',
        'django-predicate'
    ],
)
