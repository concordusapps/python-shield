# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import operator
import six


class Predicate(object):

    def __init__(self, base, attribute=None, **kwargs):

        #! Base is the base-of-reference for the predicate. This is either
        #! a constant reference or nothing (to indicate the target to
        #! be later set).
        self.base = base

        #! The attribute is the attribute reference path from the base.
        self.attribute = attribute

        # If the attribute is None and the base is of type <str> then
        # the base is None and attribute is the base.
        if not self.attribute and isinstance(self.base, six.string_types):
            self.attribute = self.base
            self.base = None

        #! Arguments are arguments to filter the attribute by.
        self.arguments = kwargs

    def __eq__(self, other):
        return BinaryExpression(self, other, operator.eq)

    def __ne__(self, other):
        return BinaryExpression(self, other, operator.ne)

    def __lt__(self, other):
        return BinaryExpression(self, other, operator.lt)

    def __le__(self, other):
        return BinaryExpression(self, other, operator.le)

    def __gt__(self, other):
        return BinaryExpression(self, other, operator.gt)

    def __ge__(self, other):
        return BinaryExpression(self, other, operator.ge)

    def in_(self, other):
        return BinaryExpression(self, other, operator.contains)

    def __and__(self, other):
        return BinaryExpression(self, other, operator.and_)

    def __or__(self, other):
        return BinaryExpression(self, other, operator.or_)

    def __invert__(self):
        return UnaryExpression(self, operator.invert)


class BinaryExpression(Predicate):

    def __init__(self, lhs, rhs, operator):
        self.lhs = lhs
        self.rhs = rhs
        self.operator = operator


class UnaryExpression(Predicate):

    def __init__(self, predicate, operator):
        self.predicate = predicate
        self.operator = operator
