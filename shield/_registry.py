# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
# from six.moves import filter as ifilter
import six


class InheritableDict(dict):
    """A dictionary that tests inheritance of keys when one cannot be found.
    Expects an iterable key format (like a tuple).  The constructor takes
    indexes for the keys that need inheritance checked.
    """
    def __init__(self, *positions):
        self.positions = positions

    def __missing__(self, key):

        for item in six.iterkeys(self):
            for position in self.positions:
                if not issubclass(key[position], item[position]):
                    break
            else:
                return self[item]
        else:
            raise KeyError(key)


class CachedRegistry(InheritableDict):
    """The key format is (<bearer>[, <target>][, <permission>])
    """

    def __init__(self):

        # key format: (bearer, target)
        self.target = InheritableDict(0, 1)

        # key format: (bearer, permission)
        self.bearer = InheritableDict(1)

        super().__init__(0, 1)

    def _maybe_cache(self, key, value):
        # TODO: Figure out if we actually need to cache.
        self[key] = value

    def __missing__(self, key):
        # Assert the type of permission being checked and ferry it off
        # elsewhere.
        # This class only accepts explict permissions on an explicit target.
        if len(key) != 3:
            value = self._dispatch(key)
        else:
            value = super().__missing__(key)

        self._maybe_cache(key, value)
        return value

    def _lookup(self, bearer, target=None, permission=None):
        """Lookup the proper registry for this permission.
        Returns (<registry>, <key>) where registry is the proper lookup
        and key is the generated key to use for the permission."""

        if target is None and permission is None:
            raise TypeError('Must specify either target or permission.')

        if target is None:
            key = (bearer, permission)
            lookup = self.target

        elif permission is None:
            key = (bearer, target)
            lookup = self.bearer

        else:
            key = (bearer, target, permission)
            lookup = self

        return lookup, key

    def retrieve(self, *args, **kwargs):
        """Retrieve the permsission function for the provided things.
        """

        lookup, key = self._lookup(*args, **kwargs)

        return lookup[key]

    def register(self, function, *permissions, bearer=None, target=None):

        # Python2 doesn't allow for mandatory kwargs :(
        if bearer is None:
            raise TypeError('bearer must be provided.')

        if target is None and not len(permissions):
            raise TypeError(
                'Cannot register a rule without either a permission or a '
                'target.')

        if not len(permissions):
            reg, key = self._lookup(bearer, target)
            reg[key] = function
        else:
            for perm in permissions:
                reg, key = self._lookup(bearer, target, perm)

registry = CachedRegistry()
