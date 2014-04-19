# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six


class InheritableDict(dict):
    """A dictionary that tests inheritance of keys when one cannot be found.
    Expects an iterable key format (like a tuple).  The constructor takes
    indexes for the keys that need inheritance checked.
    """
    def __init__(self, *positions):
        self.__positions = set(positions)

    def __missing__(self, key):
        # key = (<class1>, <class2>, <class3>)
        for bkey in six.iterkeys(self):
            # bkey = (<cls1>, <cls2>, <clss3>)
            for index, item in enumerate(bkey):
                # index = 0, item = <cls1>
                if index in self.__positions:
                    # issubclass(<class1>, <cls1>)
                    if not issubclass(key[index], item):
                        break

                else:
                    # <class1> == <cls1>
                    if key[index] != item:
                        break
            else:
                # issubclass and == passed.
                return self[bkey]
        else:
            # issubclass and == did not pass for any entries.
            raise KeyError(key)


class CachedDict(InheritableDict):

    def _maybe_cache(self, key, value):
        # Specific rules can be flagged as not cached.
        # NOTE: Right now this expects the value to be a Rule type.
        # Could be refactored somehow...
        if value.cache:
            self[key] = value

    def __missing__(self, key):
        # Assert the type of permission being checked and ferry it off
        # elsewhere.
        # This class only accepts explict permissions on an explicit target.
        value = super().__missing__(key)
        self._maybe_cache(key, value)
        return value


class Registry(CachedDict):
    """The key format is (<bearer>[, <target>][, <permission>])
    """

    def __init__(self):

        # key format: (bearer, target)
        self.target = CachedDict(0, 1)

        # key format: (bearer, permission)
        self.bearer = CachedDict(0)

        super().__init__(0, 1)

    def clear(self):
        super().clear()
        self.target.clear()
        self.bearer.clear()

    def _lookup(self, bearer, target=None, permission=None):
        """Lookup the proper registry for this permission.
        Returns (<registry>, <key>) where registry is the proper lookup
        and key is the generated key to use for the permission."""

        if target is None:
            key = (bearer, permission)
            lookup = self.bearer

        elif permission is None:
            key = (bearer, target)
            lookup = self.target

        else:
            key = (bearer, target, permission)
            lookup = self

        return lookup, key

    def retrieve(self, *args, **kwargs):
        """Retrieve the permsission function for the provided things.
        """

        lookup, key = self._lookup(*args, **kwargs)

        return lookup[key]

    # def register(self, function, *permissions, bearer=None, target=None):
    def register(self, rule):

        # Python2 doesn't allow for mandatory kwargs :(
        if rule.bearer is None:
            raise TypeError('bearer must be provided.')

        if rule.target is None and rule.permission is None:
            raise TypeError(
                'Cannot register a rule without either a permission or a '
                'target.')

        reg, key = self._lookup(rule.bearer, rule.target, rule.permission)
        reg[key] = rule


# Create the global registry we'll use for all shield permissions.
registry = Registry()
