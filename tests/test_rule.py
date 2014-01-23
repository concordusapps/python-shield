# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import pytest
import shield


class BaseTestBearer:

    def test_bearer_has(self):
        u = self.Bearer(id=7)

        assert shield.has('luck', bearer=u)

    def test_bearer_has_not(self):
        u = self.Bearer(id=6)

        assert not shield.has('luck', bearer=u)

    def test_bearer_has_unknown(self):
        u = self.Bearer(id=7)

        assert not shield.has('luck2', bearer=u)

    def test_bearer_filter_unknown(self):
        clause = shield.filter('luck2', bearer=self.Bearer)

        assert not clause


class BaseTestTarget:

    def test_bearer_target_has(self):
        u = self.Bearer(id=7)
        b = self.Target(owner_id=7)

        assert shield.has('read', bearer=u, target=b)

    def test_bearer_target_has_not(self):
        u = self.Bearer(id=7)
        b = self.Target(owner_id=3)

        assert not shield.has('read', bearer=u, target=b)

    def test_bearer_target_has_unknown(self):
        u = self.Bearer(id=7)
        b = self.Target(id=63, owner_id=7)

        assert not shield.has('write', bearer=u, target=b)

    def test_bearer_target_filter_unknown(self):
        u = self.Bearer(id=7)
        clause = shield.filter('luck2', bearer=u, target=models.Book)

        assert not clause


class BaseTestTargetExpression:

    def test_bearer_target_expression_has_not(self):
        u = self.Bearer(id=7)
        b = self.Book(owner_id=7)

        assert not shield.has('read', bearer=u, target=b)
