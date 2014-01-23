# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from .utils import register
from . import registry


class Rule(object):

    def __init__(self, function, permissions, bearer, target):
        self.function = function
        self.permissions = permissions
        self.bearer = bearer
        self.target = target

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def expression(self, func):
        # Registers an specific expression for this rule object.
        for permission in self.permissions:
            registry.expression[self.bearer, self.target, permission] = func

        # Return the function.
        return func


class rule(object):

    def __init__(self, *args, **kwargs):
        #! The positional arguments is the set of permissions to
        #! be registered from this declarative rule.
        self.permissions = args

        #! Bearer is the entity in which the permissions are being
        #! granted to.
        self.bearer = kwargs['bearer']

        #! Target is an optional parameter that causes the rule
        #! to be specifically applied to the target Entity.
        self.target = kwargs.get('target')

    def __call__(self, function):
        # Register the passed function as a rule for each permission.
        register(function, *self.permissions,
                 bearer=self.bearer,
                 target=self.target)

        # Return a wrapped rule function.
        return Rule(function, self.permissions, self.bearer, self.target)
