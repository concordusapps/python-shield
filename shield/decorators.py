# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from .utils import register
from ._registry import registry, expression
from functools import reduce
import operator


class Rule(object):

    def __init__(self, function, permissions, bearer, target):
        self.function = function
        self.permissions = permissions
        self.bearer = bearer
        self.target = target

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def expression(self, func):
        # Registers a specific expression for this rule object.
        for permission in self.permissions:
            expression[self.bearer, self.target, permission] = func

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


def deferred_rule_for(permission, attributes, bearer, target=None):
    from .predicate import Predicate

    @rule(permission, bearer=bearer, target=target)
    def method(target_, bearer_):
        q = []
        for attribute in attributes:

            # Resolve the class on the remote side.
            if isinstance(target_, type):
                attr = getattr(target_, attribute)
            else:
                attr = getattr(target_.__class__, attribute)

            cls = attr.property.mapper.class_

            # Find the rule for that class.
            if permission:
                key = (bearer, cls, permission)
            else:
                key = (bearer, cls)

            defer = registry[key]

            # Append the predicate for it.
            q.append(defer(Predicate(target_, attribute), bearer_))

        return reduce(operator.and_, q)


def deferred_rule(*permissions, **kwargs):
    kwargs.setdefault('target', None)
    if permissions:
        for permission in permissions:
            deferred_rule_for(permission, **kwargs)

    else:
        deferred_rule_for(None, **kwargs)
