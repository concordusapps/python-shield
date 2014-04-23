# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from six.moves import reduce
from ._registry import registry
from sqlalchemy.orm import object_session
from sqlalchemy import sql
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
    target = kwargs.get('target')
    bearer_cls = type_for(bearer)

    # We need a query object.  There are many ways to get one,  Either we can
    # be passed one, or we can make one from the session.  We can either be
    # passed the session, or we can grab the session from the bearer passed.

    if 'query' in kwargs:
        query = kwargs['query']
    elif 'session' in kwargs:
        query = kwargs['session'].query(target)
    else:
        query = object_session(bearer).query(target)

    getter = functools.partial(
        registry.retrieve,
        bearer=bearer_cls,
        target=target)

    try:
        # Generate a hash of {rulefn: permission} that we can use later
        # to collect all of the rules.
        if len(permissions):
            rules = {getter(permission=x): x for x in permissions}
        else:
            rules = {getter(): None}
    except KeyError:
        # No rules defined.  Default to no permission.
        return query.filter(sql.false())

    # Invoke all the rules and collect the results

    # Abusing reduce here to invoke each rule and send the return value (query)
    # from one rule to the next one.  In this way the query becomes
    # increasingly decorated as it marches through the system.

    # q == query
    # r = (rulefn, permission)
    reducer = lambda q, r: r[0](permission=r[1], query=q, bearer=bearer)

    return reduce(reducer, six.iteritems(rules), query)


def has(*permissions, **kwargs):
    """
    Checks if the passed bearer has the passed permissions (optionally on
    the passed target).
    """

    target = kwargs['target']

    kwargs['target'] = type_for(target)

    # TODO: Predicate evaluation?
    return target in filter_(*permissions, **kwargs)
