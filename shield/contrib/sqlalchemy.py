# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
from shield.predicate import Predicate, BinaryExpression, UnaryExpression
from sqlalchemy.orm.attributes import QueryableAttribute
import six
import operator
from collections import defaultdict
from itertools import chain


def evaluate_expression(expression, target=None):

    # Evaluate our operands.
    lhs = evaluate(expression.lhs, target)
    rhs = evaluate(expression.rhs, target)

    # Expand the operands.
    base = None
    attribute = lhs
    if isinstance(lhs, tuple):
        base, attribute = lhs

    if expression.operator == operator.contains:

        if hasattr(attribute, 'class_'):
            # We are actually an instrumented attribute.

            # Get the referenced foriegn key and create the in clause on it.
            q = attribute.expression.right
            items = list(chain(*rhs.values(attribute.expression.left)))
            if not items:
                return False

            result = q.in_(items)

            if base:
                return base.has(result)

            return result

        else:
            # We're just a target; flip and continue.
            rhs, attribute = attribute, rhs

    result = expression.operator(attribute, rhs)

    if base:
        return base.has(result)

    return result


def evaluate_unary(predicate, target):
    return predicate.operator(evaluate(predicate.predicate, target))


def evaluate(predicate, target=None):

    if isinstance(predicate, BinaryExpression):
        return evaluate_expression(predicate, target)

    if isinstance(predicate, UnaryExpression):
        return evaluate_unary(predicate, target)

    elif isinstance(predicate, Predicate):

        # Resolve the base of reference (either the constant or the
        # passed one).
        base = predicate.base or target
        if isinstance(base, Predicate):
            base = evaluate(base, target)

        if isinstance(base, QueryableAttribute):
            return getattr(
                base.property.mapper.class_, predicate.attribute)

        else:
            obj = getattr(base, predicate.attribute)

        # Collect the arguments in a map from the table to the key and value.
        arguments_map = defaultdict(dict)

        # is_active=False
        # arguments_map[None] = {'is_active': False}

        # membership__is_active=True
        # arguments_map['membership'] = {'is_active': True}

        for argument, value in six.iteritems(predicate.arguments):
            key = None
            if '__' in argument:
                key, argument = argument.split('__', 1)
            arguments_map[key][argument] = value

        # Figure out the registry.

        try:
            ref = '_decl_class_registry'
            reg = getattr(base, ref, getattr(type(base), ref))

        except AttributeError:
            reg = None

        # Apply the filtering for the arguments.

        for key, arguments in six.iteritems(arguments_map):
            if key:
                obj = obj.join(reg[key])

            obj = obj.filter_by(**arguments)

        return obj

    return predicate
