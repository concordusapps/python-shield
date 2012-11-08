#! /usr/bin/env python
import os
from setuptools import setup, find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
        name='shield',
        version=read('VERSION'),
        description='',
        long_description=read('README.md'),
        author='Concordus Applications',
        author_email='support@concordusapps.com',
        url='http://github.com/concordusapps/django-shield',
        package_dir={'shield': 'src/shield'},
        packages=find_packages('src')
    )
