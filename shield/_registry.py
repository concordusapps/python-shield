# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six


class InheritableDict(dict):
    """A dictionary that tests inheritance of keys when one cannot be found.
    Expects an iterable key format (like a tuple).  The constructor takes
    a single index into the keys that need inheritance checked.
    """
    def __init__(self, position):
        self.__position = position

    def __missing__(self, key):
        # key = (<class1>, <class2>, <class3>)

        derived = key[self.__position]
        results = []

        for bkey in six.iterkeys(self):
            # bkey = (<base1>, <base2>, <base3>)
            for index, item in enumerate(bkey):
                # index = 0, item = <base1>
                if index == self.__position:
                    # issubclass(<class1>, <base1>)
                    if not issubclass(derived, item):
                        break
                else:
                    # <class1> == <base1>
                    if key[index] != item:
                        break
            else:
                # issubclass and == passed
                results.append(bkey)
        else:
            if len(results):
                # We found results.  Evaluate the MRO for these entries and
                # chose the one the farthest down the MRO chain (the most
                # derived superclass.)

                # We can accomplish this by checking the index of the
                # superclasses in the mro chain of the keyed class.
                mro = derived.mro()

                getter = lambda x: mro.index(x[self.__position])
                indexes = {getter(x): x for x in results}

                # MRO is ordered most derived first.  So sort the keys and
                # use the lowest keys to find the final result
                result_key = sorted(six.iterkeys(indexes))[0]
                return self[indexes[result_key]]

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
        value = super(CachedDict, self).__missing__(key)
        self._maybe_cache(key, value)
        return value


class Registry(CachedDict):
    """The key format is (<bearer>[, <target>][, <permission>])
    """

    def __init__(self):

        # key format: (bearer, target)
        self.target = CachedDict(1)

        # key format: (bearer, permission)
        # No inheritance shenannigans apply to the bearer registry, so we
        # don't need to cache the results either.
        self.bearer = dict()

        super(Registry, self).__init__(1)

    def clear(self):
        super(Registry, self).clear()
        self.target.clear()
        self.bearer.clear()

    def __missing__(self, key):
        try:
            result = super(Registry, self).__missing__(key)
        except KeyError:
            # Try looking it up as a <bearer HAS ALL PERMISSIONS ON target>
            # style permission
            # Our key format is (bearer, target, permission)
            # Target registry's permission is (bearer, target)
            result = self.target[(key[0], key[1])]
            self._maybe_cache(key, result)

        return result

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
