# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
from . import registry


class rule:
    """Add the decorated rule to our registry.  The rule function's signature
    should look like this:

    foo(query, owner, target)

    where query is the sqlalchemy query object, owner is an instance of the
    owner permission, and target is an instance of the targeted object.
    The function should return either a query object with permission
    information added to it.
    """

    def __init__(self, *perms, **kwargs):
        """owner: The owner of the permissions.
        permissions: The set of permissions that the owner has
        target: The model that we are checking if the owner has permissions for
        """
        # Owner is a mandatory kwarg param
        self.owner = kwargs['owner']

        # Target is an optional param used to denote what registry the
        # decorated function goes into
        self.target = kwargs.get('target')

        # The permission list!
        self.permissions = perms

    def __call__(self, fn):
        """Add the passed function to the registry
        """
        for perm in self.permissions:
            # If we have no target, this goes into the general registry
            # otherwise it goes into the targeted registry
            if self.target is None:
                registry.general[(self.owner, perm)] = fn
            else:
                registry.targeted[(self.owner, perm, self.target)] = fn

        # We really have no reason to keep the wrapper now that we have added
        # the function to the registry
        return fn
