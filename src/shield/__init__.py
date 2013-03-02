# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import functools
import inspect
from .rules import registry


class _wrapper:

    def __init__(self, permissions, function):
        self.function = function
        self.permissions = permissions


class rule:

    def __init__(self, *permissions):
        self.permissions = permissions

    def __call__(self, function):
        return _wrapper(self.permissions, function)


def rules(cls):
    for name, member in inspect.getmembers(cls):
        if isinstance(member, _wrapper):
            method = functools.partial(member.function, cls)
            for permission in member.permissions:
                registry[(permission, cls)] = method

    return cls
