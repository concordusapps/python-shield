# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import operator
from six.moves import map, reduce
from . import registry


def register(function, *permissions, **kwargs):
    """Registers the passed function with the passed permissions.

    @param[in] function
        The function the register.

    @param[in] permissions
        The permissions to register for the bearer.

    @param[in] bearer
        The entity that is being granted the permissions.

    @param[in] target
        The entity that the bearer is being granted the
        permissions for (optional).
    """
    target, bearer = kwargs.get('target'), kwargs['bearer']
    for permission in permissions:
        key = bearer, target, permission
        registry.rule[key] = function
        registry.expression[key] = function


def has(*permissions, **kwargs):
    """
    Checks if the passed bearer has the passed permissions (optionally on
    the passed target).
    """
    target, bearer = kwargs.get('target'), kwargs['bearer']
    bearer_cls = bearer.__class__
    store = registry.rule

    if target is None:
        check = lambda p: store[bearer_cls, None, p](bearer)

    else:
        target_cls = target.__class__
        check = lambda p: store[bearer_cls, target_cls, p](target, bearer)

    try:
        # Attempt to check rules.
        return reduce(operator.and_, map(check, permissions))

    except KeyError:
        # Rule not defined; return False.
        return False


def filter(*permissions, **kwargs):
    """
    Constructs a clause to filter all bearers or targets for a given
    berarer or target.
    """
    target, bearer = kwargs.get('target'), kwargs['bearer']
    store = registry.expression
    bearer_cls = bearer.__class__ if not isinstance(bearer, type) else bearer

    if target is None:
        check = lambda p: store[bearer_cls, None, p](bearer_cls)

    else:
        target_cls = target if isinstance(target, type) else target.__class__
        key = lambda x: (bearer_cls, target_cls, x)
        check = lambda x: store[key(x)](target_cls, bearer_cls)

    try:
        # Attempt to build clause.
        return reduce(operator.and_, map(check, permissions))

    except KeyError:
        # Rule not defined; return False.
        return False
