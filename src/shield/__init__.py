# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import functools
import inspect
from .rules import registry


class _wrapper:

    def __init__(self, permission, function):
        self.function = function
        self.permission = permission


class rule:

    def __init__(self, permission):
        self.permission = permission

    def __call__(self, function):
        return _wrapper(self.permission, function)


def rules(cls):
    for name, member in inspect.getmembers(cls):
        if isinstance(member, _wrapper):
            registry[(member.permission, cls)] = functools.partial(
                member.function, cls)

    return cls
