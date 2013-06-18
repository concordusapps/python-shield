# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

# Keys of this dictionary are python tuples.  This works because in python,
# a tuple's hash function returns a has based on the contents of the tuple
# rather than an identifier for the memory.

# The key format is (owner, permission, target), ex:
# (User, 'read', Document) where User has 'read' permissions on Document
registry = {}
