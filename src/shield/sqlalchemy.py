# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
from sqlalchemy.orm import class_mapper
from functools import reduce
from . import registry
import operator


def check_perm(session, reg, key, fn, owner, target):
    """Does the permsission checking"""

    # If there is no permission function then just assume that access is
    # denied.
    if not key in reg:
        return False

    # Call the function
    return fn(reg[key], owner, target)


def normalize(owner, target):
    """Normalize execution paths by providing callables for the differences
    in execution.  Returns lookup registry, key building callable, and
    permission function callable."""
    # Figure out if we're doing general permissions or targeted permissions
    if target is None:
        # If the target is none, then we're checking to see if the owner has
        # these permissions, rather than the target itself.
        target = owner
        key = lambda p: (owner.__class__, p)
        call = lambda fn, o, t: fn(o)
        reg = registry.general
    else:
        key = lambda p: (owner.__class__, p, target.__class__)
        call = lambda fn, o, t: fn(o, t)
        reg = registry.targeted

    # Return it
    return reg, key, call, target


def exists(queryset, obj):
    """Return boolean if the object exists inside the sqlalchemy queryset."""

    # Get the primary keys for for the object
    mapper = class_mapper(obj.__class__)
    columns = mapper.primary_key

    # Create a getter that gets the value of the column and checks equality.
    get = mapper.get_property_by_column
    value_getter = lambda x: x == get(x).class_attribute.__get__(obj, None)

    # Reduce them to a single statement via AND
    filter_param = reduce(operator.and_, map(value_getter, columns))

    # Check to see if it exists in the result set.
    return queryset.filter(filter_param).first() is not None


def has_perm(session, owner, perm, target=None):
    """Check to see if the owner has permissions on the target."""

    # Translate the arguments into more interesting registry information
    reg, key_builder, fn, target = normalize(owner, target)

    # Do the permission checking
    session = check_perm(session, reg, key_builder(perm), fn, owner, target)

    return exists(session, target)


def has_perms(session, owner, perms, target=None):
    """Same as has_perm, but for an iterable set of permissions."""

    # Translate the arguments into registry information
    reg, key_builder, fn, target = normalize(owner, target)

    for perm in perms:
        # Build the key for these perms
        key = key_builder(perm)

        # Replace the session for each, further limiting the results
        session = check_perm(session, reg, key, fn, owner, target)

    return exists(session, target)


# shield.has_perm(user, 'can_jump', target)
# shield.has_perms(user, ['can_jump'], target)

# shield.has_perms(user, ['can_jump'], target)
