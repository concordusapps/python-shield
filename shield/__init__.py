# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from ._version import __version__, __version_info__  # noqa
from .decorators import rule, deferred_rule
from .utils import has
from .utils import filter_ as filter
from ._registry import registry


register = registry.register


__all__ = [
    'rule',
    'deferred_rule',
    'has',
    'filter',
    'register'
]
