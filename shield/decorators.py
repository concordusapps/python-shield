# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from ._registry import registry
from six.moves import map, reduce
import operator


class Rule(object):
    """Rule entry object (sits in the registry).  Invokes rule when invoked,
    and returns the rule."""

    def __init__(self, function, permission, bearer, target, cache=True):
        self.function = function
        self.cache = cache
        self.bearer = bearer
        self.target = target
        self.permission = permission

    def __call__(self, query, bearer):
        args = {
            'query': query,
            'bearer': bearer,
            # 'target': self.target,
        }
        return self.function(**args)


class DeferredRule(Rule):
    """Deferred type registry rule."""

    def __init__(self, *args, **kwargs):
        self.attributes = kwargs['attributes']
        super().__init__(*args, **kwargs)

    @property
    def attr_map(self):
        # This is the cached attribute map.
        if not hasattr(self, '_attr_map'):
            class_for = lambda x: getattr(self.bearer).property.mapper.class_
            self._attr_map = {x: class_for(x) for x in self.attributes}
        return self._attr_map

    def __call__(self, query, bearer):
        rules = []
        for name, class_ in self.attr_map:
            rule = registry.retrieve(
                bearer=self.bearer,
                target=class_,
                permission=self.permission)
            rule.append(rules)

        # Invoke all the rules.
        # TODO: jointables here.
        return reduce(operator.and_, map(lambda x: x(query, bearer), rules))


class rule(object):
    """Rule registration object."""

    _rule_class = Rule

    def __init__(self, *permissions, **kwargs):
        # The positional arguments is the set of permissions to
        # be registered from this declarative rule.
        self.permissions = permissions

        # Bearer is the entity in which the permissions are being
        # granted to.
        self.bearer = kwargs['bearer']

        # Target is an optional parameter that causes the rule
        # to be specifically applied to the target Entity.
        self.target = kwargs.get('target')

        # Set this to true if you discover that the cache is growing enormous
        # due to too many combinations of a specific rule being cached.
        self.cache = kwargs.get('cache', True)

    def __call__(self, function):
        # Register the passed function as a rule for each permission.

        # Common arguments to the registration function.
        args = {
            'function': function,
            'target': self.target,
            'cache': self.cache,
            'bearer': self.bearer,
        }

        # If no permissions were specified, then still register a generic
        # permission.
        if not len(self.permissions):
            registry.register(self._rule_class(permission=None, **args))
        else:
            for perm in self.permissions:
                registry.register(self._rule_class(permission=perm, **args))

        return function


class deferred_rule(rule):

    _rule_class = DeferredRule

    def __init__(self, *args, **kwargs):
        # A list of all the attributes that we should defer rule resolution
        # for.
        self.attributes = kwargs['attributes']
