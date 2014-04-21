# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import operator
from six.moves import reduce
from ._registry import registry
from sqlalchemy.orm import object_session
import functools
import six


def type_for(obj):
    return obj if isinstance(obj, type) else obj.__class__


def filter_(*permissions, **kwargs):
    """
    Constructs a clause to filter all bearers or targets for a given
    berarer or target.
    """
    bearer = kwargs['bearer']
    session = kwargs.get('session', object_session(bearer))
    target = kwargs.get('target')

    query = session.query(target)

    bearer_cls = type_for(bearer)

    getter = functools.partial(
        registry.retrieve,
        bearer=bearer_cls,
        target=target)

    try:
        # Generate a hash of {rule_fn: permission} that we can use later
        # to collect all of the rules.
        if len(permissions):
            fns = {getter(permission=x): x for x in permissions}
        else:
            fns = {getter(): None}
    except KeyError:
        # No rules defined.  Default to no permission.
        return False

    params = {
        'query': query,
        'bearer': bearer,
    }

    # Invoke all the rules and collect the results
    results = (x(permission=y, **params) for x, y in six.iteritems(fns))

    # AND the results together and return the resulting query.
    # what does it even mean to AND these together in sqlalchemy?
    return reduce(operator.and_, results)


def has(*permissions, **kwargs):
    """
    Checks if the passed bearer has the passed permissions (optionally on
    the passed target).
    """

    target = kwargs['target']

    kwargs['target'] = type_for(target)

    # TODO: Predicate evaluation?
    return target in filter_(*permissions, **kwargs)
