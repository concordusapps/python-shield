# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from ._registry import registry
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


class rule(object):

    def __init__(self, *permissions, bearer, target=None):
        #! The positional arguments is the set of permissions to
        #! be registered from this declarative rule.
        self.permissions = permissions

        #! Bearer is the entity in which the permissions are being
        #! granted to.
        self.bearer = bearer

        #! Target is an optional parameter that causes the rule
        #! to be specifically applied to the target Entity.
        self.target = target

    def __call__(self, function):
        # Register the passed function as a rule for each permission.
        registry.register(
            function,
            *self.permissions,
            bearer=self.bearer,
            target=self.target)

        # Return a wrapped rule function.
        return Rule(function, self.permissions, self.bearer, self.target)


def deferred_rule_for(permission, attributes, bearer, target=None):
    from .predicate import Predicate

    args = {'bearer': bearer, 'target': target}

    # Change how we decorate the child method depending on the type of
    # permission being registered.  Additionally, change the kind of key
    # we're generating to look up the keys in shield's registry.
    if permission is None:
        decorator = rule(**args)
        maker = lambda x: (bearer, x)
    else:
        decorator = rule(permission, **args)
        maker = lambda x: (bearer, x, permission)

    # look up the remote side of the attributes (not the sqlalchemy queryable,
    # but the object it represents.)
    # TODO: make this unspecific for sqlalchemy.
    attrs = [getattr(target, x).property.mapper.class_ for x in attributes]

    # Create a cache of the lookup keys.
    keys = [maker(x) for x in attrs]

    @decorator
    def method(target_, bearer_):
        q = []
        for key, attribute in zip(keys, attributes):

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
