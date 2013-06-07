# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

# Two way permission registry.  For testing if an object has a permission on
# a different object.
# This is set up in the following format.
# {
#     owner: {
#         target: {
#             permission: function,
#         }
#     }
# }
dual = {}

# One way permission registry.  For checking if an object is part of a
# permission group.
# This is set up in the following format.
# {
#     owner: {
#         permission: function,
#     }
# }
single = {}


def dual_add(owner, target, permission, function):
    """Add a permission method to the dual hash"""

    # Unwrap all the dictionaries
    owner_dict = dual.get(owner, {})
    target_dict = owner_dict.get(target, {})

    # Set the permission
    target_dict[permission] = function

    # Wrap them back up
    owner_dict[target] = target_dict
    dual[owner] = owner_dict


def single_add(owner, permission, function):
    """Add a permission method to the single hash"""
    owner_dict = single.get(owner, {})
    owner_dict[permission] = function
    single[owner] = owner_dict
