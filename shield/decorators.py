# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from ._registry import registry
from six.moves import reduce
import operator
import six


class RuleBase(object):

    def __init__(self, permission, bearer, target, cache=True):
        self.permission = permission
        self.bearer = bearer
        self.target = target
        self.cache = cache


class Rule(RuleBase):
    """Rule entry object (sits in the registry).  Invokes rule when invoked,
    and returns the rule."""

    def __init__(self, *args, **kwargs):
        self.function = kwargs.pop('function')
        super(Rule, self).__init__(*args, **kwargs)

    def __call__(self, query, bearer):
        args = {
            'query': query,
            'bearer': bearer,
            'target': self.target,
        }
        return self.function(**args)


class DeferredRule(RuleBase):
    """Deferred type registry rule."""

    def __init__(self, *args, **kwargs):
        self.attributes = kwargs.pop('attributes')
        super(DeferredRule, self).__init__(*args, **kwargs)

    @property
    def attr_map(self):
        # This is the cached attribute map.
        if not hasattr(self, '_attr_map'):
            cls_for = lambda x: getattr(self.target, x).property.mapper.class_
            self._attr_map = {x: cls_for(x) for x in self.attributes}
        return self._attr_map

    def __call__(self, query, bearer):
        rules = {}
        for name, class_ in six.iteritems(self.attr_map):
            rule = registry.retrieve(
                bearer=self.bearer,
                target=class_,
                permission=self.permission)
            rules[rule] = class_

        # Invoke all the rules.
        def join_table(rule, class_):
            return rule(query.join(class_), bearer)

        results = (join_table(*x) for x in six.iteritems(rules))
        return reduce(operator.and_, results)


class rule(object):
    """Rule registration object."""

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
            registry.register(Rule(permission=None, **args))
        else:
            for perm in self.permissions:
                registry.register(Rule(permission=perm, **args))

        return function


def deferred_rule(*permissions, **kwargs):

    # Create a bunch of deferred rules,
    if permissions is None:
        rules = [DeferredRule(permission=None, **kwargs)]
    else:
        rules = [DeferredRule(permission=x, **kwargs) for x in permissions]

    # Register them all!
    for rule in rules:
        registry.register(rule)
