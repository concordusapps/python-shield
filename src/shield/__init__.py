# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import inspect
from . import registry


class _method_wrapper(object):
    """A placeholder object used to wrap methods until the rules decorator
    comes around and adds everything to the shield registry."""

    def __init__(self, fn, permissions, owner, target):
        self.permissions = permissions
        self.owner = owner
        self.target = target
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
        return _method_wrapper(fn, self.permissions, self.owner, self.target)


def rules(cls):
    """Add all permission methods on the decorated object to our registry."""
    # This is called after the class object is instantiated and all methods are
    # wrapped with the decorator.  Iterate over all of our personal wrapped
    # methods, unwrap them, and add them to the registry.

    mems = inspect.getmembers(cls, lambda x: isinstance(x, _method_wrapper))

    for name, member in mems:
        # Unwrap each method
        # Add the member to the registry
        for perm in member.permissions:
            registry.registry[(member.owner, perm, member.target)] = member.fn

        # Now that the method has been added to the registry, unwrap the method
        # since we don't need the wrapper anymore.
        setattr(cls, name, member.fn)
