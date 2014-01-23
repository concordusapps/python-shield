# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import six


class Registry(dict):
    """A rule registry dictionary.

    The key format is (<bearer>[, <target>][, <permission>])
    """

    def __missing__(self, key):
        # No specific rule; iterate through and attempt to use
        # inheritance to find a rule.
        strs = six.string_types
        cls = key[-2] if isinstance(key[-1], strs) else key[-1]
        for bkey, base_rule in six.iteritems(self):
            bcls = bkey[-2] if isinstance(bkey[-1], strs) else bkey[-1]
            if issubclass(cls, bcls):
                break

        else:
            if isinstance(key[-1], six.string_types):
                # No rule is defined for this rule check if we are
                # permission-specific and then check for a matching global rule.
                global_key = key[:-1]
                value = self[key] = self[global_key]
                return value

            raise KeyError

        # Use the base class.
        value = self[key] = base_rule
        return value


registry = Registry()


class ExpressionRegistry(dict):
    """An expression registry dictionary.

    The key format is (<bearer>[, <target>][, <permission>])
    """

    def __missing__(self, key):
        return registry[key]


expression = {}
