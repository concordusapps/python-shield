# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from six.moves import filter as ifilter
import six


class BearerRegistry(dict):
    """Key is (<bearer>, <permission>)"""


bearer_registry = BearerRegistry()


class TargetRegistry(dict):
    def __missing__(self, key):
        """Keys is (<bearer>, <target>)"""
        # Delegate to the bearer registry if this is a generic permission check
        if len(key) < 2:
            return bearer_registry[key]

        bearer, target = key

        # Iterate over keys where the bearer matches the bearer we were given.
        for base_key in ifilter(lambda x: bearer == x[0], six.iterkeys(self)):
            # Is target a subclass of a base target we have stored
            if issubclass(target, base_key[1]):
                rule = self[base_key]
                break
        else:
            raise KeyError(key)

        self[key] = rule
        return rule


target_registry = TargetRegistry()


class PermissionRegistry(dict):
    def __missing__(self, key):
        """Key format is (<bearer>, <target>, <permission>)"""
        # Delegate to the target registry if this is not an individual
        # permission check
        if len(key) < 3:
            return target_registry[key]

        bearer, target, permission = key

        # This should probably be moved elsewhere
        if target is None:
            return bearer_registry[bearer, permission]

        # We only want to iterate over items where the bearer and permission
        # matches.
        check_bearer = lambda x: bearer == x[0]
        check_perm = lambda x: permission == x[2]
        check = lambda x: all((check_bearer(x), check_perm(x)))

        for base_key in ifilter(check, six.iterkeys(self)):
            base_bearer, base_target, base_perm = base_key

            # Inheritance check for the target.
            if issubclass(target, base_target):
                # Found a match!
                rule = self[base_key]
                break
        else:
            # No entry found, check the target registry.
            rule = target_registry[bearer, target]

        self[key] = rule
        return rule


registry = PermissionRegistry()


class ExpressionRegistry(dict):
    """An expression registry dictionary.

    The key format is (<bearer>[, <target>][, <permission>])
    """

    def __missing__(self, key):
        return registry[key]


expression = ExpressionRegistry()
