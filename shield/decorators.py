# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from ._registry import registry
from six.moves import reduce
import operator
import six


class RuleBase(object):
    # __call__ invoked with the following
    # query: sqlalchemy query object aspected to the target.
    # target: target class defined with the rule.
    # bearer: bearer instance of type defined with the rule
    # permission: Permission being checked.

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

    def __call__(self, **kwargs):
        kwargs['target'] = self.target
        return self.function(**kwargs)


class DeferredRule(RuleBase):
    """Deferred type registry rule.  Specialized to defer specific permissions
    to another attribute"""

    def __init__(self, *args, **kwargs):
        self.attributes = kwargs.pop('attributes')
        super(DeferredRule, self).__init__(*args, **kwargs)

    @property
    def attr_map(self):
        # This is the cached attribute map.
        # This returns a hash of {'attribute': (class_, sa_column)}
        # The column is used during the join operation.
        if not hasattr(self, '_attr_map'):
            cls_for = lambda x: getattr(self.target, x).property.mapper.class_
            col_for = lambda x: getattr(self.target, x)
            attrs = self.attributes
            self._attr_map = {x: (cls_for(x), col_for(x)) for x in attrs}
        return self._attr_map

    def lookup(self, permission):
        # This is a deferred rule for a specific rule type.  Therefore,
        # we will ignore the permission argument passed, because we already
        # have our won permissions we're listening to?

        # If this deferred rule was defined with a permission, then we are in
        # (bearer, target) mode else we're in (bearer, target, permission)
        # mode.  In the former mode, we are checking any permission that
        # we recieve period.  In the latter, we're checking with whatever
        # permission we were given.

        perm = permission if self.permission is None else self.permission
        rules = {}
        for name, (class_, col) in six.iteritems(self.attr_map):
            rule = registry.retrieve(
                bearer=self.bearer,
                target=class_,
                permission=perm)
            rules[rule] = class_, col
        return rules

    def __call__(self, query, bearer, permission):
        rules = self.lookup(permission)

        params = {
            # 'query': query,
            'bearer': bearer,
            'permission': permission,
            'target': self.target
        }

        # Invoke all the rules.
        def join_table(rule, classes):
            class_, col = classes
            kwargs = dict(params)
            kwargs['query'] = query.join(class_, col)
            return rule(**kwargs)

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
    if not len(permissions):
        rules = [DeferredRule(permission=None, **kwargs)]
    else:
        rules = [DeferredRule(permission=x, **kwargs) for x in permissions]

    # Register them all!
    for rule in rules:
        registry.register(rule)
