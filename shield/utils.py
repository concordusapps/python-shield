# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import operator
from six.moves import map, reduce
from ._registry import registry
import functools


def filter_qset(*permissions, **kwargs):
    """
    Constructs a clause to filter all bearers or targets for a given
    berarer or target.
    """
    bearer = kwargs['bearer']
    target = kwargs.get('target')

    bearer_cls = bearer if isinstance(bearer, type) else bearer.__class__

    getter = functools.partial(registry.retrieve, bearer_cls, target)

    try:
        if len(permissions):
            fns = [getter(x) for x in permissions]
        else:
            fns = [getter()]
    except KeyError:
        # No rules defined.  Default to no permission.
        return False

    return reduce(operator.and_, map(lambda x: x(target, bearer), fns))


def has(*permissions, **kwargs):
    """
    Checks if the passed bearer has the passed permissions (optionally on
    the passed target).
    """

    return kwargs['bearer'] in filter_qset(*permissions, **kwargs)
