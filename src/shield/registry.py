# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

# Keys of these dictionaries are python tuples.  This works because in python,
# a tuple's hash function returns a has based on the contents of the tuple
# rather than an identifier for the memory.

# This registry is for permissions from a particular object against another
# object.  eg: User 'owns' Dog.

# The key format is (owner, permission, target), ex:
# (User, 'own', Dog) where User has 'read' permissions on Document.
targeted = {}

# This registry is for general permissions on an object.  eg: User 'superuser'
# The key format is (object, permission), ex: (User, 'superuser')
general = {}
