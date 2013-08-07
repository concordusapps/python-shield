# -*- coding: utf-8 -*-
import sys
from os import path, environ

# Get the base path.
base = path.join(path.dirname(__file__), '..')

# Append the source directory to PATH.
sys.path.append(path.join(base, 'src'))

# Set the django env variable.
environ['DJANGO_SETTINGS_MODULE'] = 'tests.shield.django_settings'
