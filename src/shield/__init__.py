# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import functools
import inspect
from . import rules


# class _wrapper:

#     def __init__(self, permissions, function):
#         self.function = function
#         self.permissions = permissions

#     def __call__(self, *args, **kwargs):
#         return self.function(*args, **kwargs)


# class rule:

#     def __init__(self, *permissions):
#         self.permissions = permissions

#     def __call__(self, function):
#         return _wrapper(self.permissions, function)


# def rules(cls):
#     for name, member in inspect.getmembers(cls):
#         if isinstance(member, _wrapper):
#             method = functools.partial(member.function, cls)
#             for permission in member.permissions:
#                 registry[(permission, cls)] = method

#     return cls


class _method_wrapper(object):

    def __init__(self, permissions, fn):
        self.permissions = permissions
        self.fn = fn

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


class rule:

    def __init__(self, owner, permissions, target=None):
        """owner: The owner of the permissions.
        permissions: The set of permissions that the owner has
        target: The model that we are checking if the owner has permissions for
        """
        self.owner = owner
        self.permissions = permissions
        self.target = target

    def __call__(self, fn):
        return _method_wrapper(self.permissions, fn)


def rules(cls):

    mems = inspect.getmembers(cls, lamdbda x: isinstance(x, _method_wrapper))
    for name, member in mems:

        # We can't add bound methods to our registry, so create partials
        # that emulate bound methods
        method = functools.partial(member.function, cls)

        # Depending on the target, add to the single or dual
        for permission in member.permissions:

            # Add the permission to the registry
            owner = registry.get(cls)
