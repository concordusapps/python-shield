# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import operator
from six.moves import map, reduce
from ._registry import registry, target_registry, bearer_registry, expression


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

    # Generic USER HAS ALL PERMISSIONS ON TARGET type permision
    if not len(permissions):
        target_registry[kwargs['bearer'], kwargs['target']] = function

    # Generic USER CAN X permission.
    elif not 'target' in kwargs:
        for perm in permissions:
            bearer_registry[kwargs['bearer'], perm] = function

    # Specific USER CAN X ON TARGET permission.
    else:
        for perm in permissions:
            registry[kwargs['bearer'], kwargs['target'], perm] = function


def has(*permissions, **kwargs):
    """
    Checks if the passed bearer has the passed permissions (optionally on
    the passed target).
    """
    target, bearer = kwargs.get('target'), kwargs['bearer']
    bearer_cls = bearer.__class__

    if target is None:
        check = lambda p: registry[bearer_cls, None, p](target, bearer)

    else:
        target_cls = target.__class__
        check = lambda p: registry[bearer_cls, target_cls, p](target, bearer)

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
    bearer_cls = bearer.__class__ if not isinstance(bearer, type) else bearer

    if target is None:
        check = lambda p: expression[bearer_cls, None, p](target, bearer_cls)

    else:
        target_cls = target if isinstance(target, type) else target.__class__
        check = lambda x: expression[bearer_cls, target_cls, x](
            target, bearer)

    try:
        # Attempt to build clause.
        return reduce(operator.and_, map(check, permissions))

    except KeyError:
        # Rule not defined; return False.
        return False
