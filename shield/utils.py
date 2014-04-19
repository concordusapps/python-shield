# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import operator
from six.moves import map, reduce
from ._registry import registry
import functools


def type_for(obj):
    return obj if isinstance(obj, type) else obj.__class__


def filter_(*permissions, **kwargs):
    """
    Constructs a clause to filter all bearers or targets for a given
    berarer or target.
    """
    bearer = kwargs['bearer']
    session = kwargs['session']
    target = kwargs.get('target')

    query = session.query(target)

    bearer_cls = type_for(bearer)

    getter = functools.partial(
        registry.retrieve,
        bearer=bearer_cls,
        target=target)

    try:
        if len(permissions):
            fns = [getter(permission=x) for x in permissions]
        else:
            fns = [getter()]
    except KeyError:
        # No rules defined.  Default to no permission.
        return False

    return reduce(operator.and_, map(lambda x: x(query, bearer), fns))


def has(*permissions, **kwargs):
    """
    Checks if the passed bearer has the passed permissions (optionally on
    the passed target).
    """

    target = kwargs['target']

    kwargs['target'] = type_for(target)

    # TODO: Predicate evaluation?
    return target in filter_(*permissions, **kwargs)
