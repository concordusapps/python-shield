# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import pytest
import shield
from shield.predicate import Predicate as P
from shield.contrib.sqlalchemy import evaluate
from . import sqlalchemy as models


class BaseTest:

    @pytest.fixture(autouse=True, scope='function')
    def database(self, request):
        meta = models.Base.metadata
        meta.create_all(models.engine)
        request.addfinalizer(lambda: meta.drop_all(models.engine))

    def setup(self):
        self.session = models.Session()


class TestSimplePredicate(BaseTest):

    def setup(self):
        super(TestSimplePredicate, self).setup()

        # Add 49 users.
        for n in range(49):
            self.session.add(models.User(name=str(n)))
            self.session.commit()

    def test_evaluate_attribute(self):
        bearer = models.User(id=7)
        q = P(bearer, 'id')

        assert evaluate(q) == bearer.id

    def test_evaluate_attribute_eq(self):
        bearer = models.User(id=7)
        q = P(bearer, 'id') == 7
        n = bearer.id == 7

        assert evaluate(q) == n

    def test_evaluate_attribute_ne(self):
        bearer = models.User(id=7)
        q = P(bearer, 'id') != 7
        n = bearer.id != 7

        assert evaluate(q) == n

    def test_evaluate_target_attribute(self):
        bearer = models.User(id=7)
        q = P('id')

        assert evaluate(q, bearer) == bearer.id

    def test_evaluate_target_attribute_eq(self):
        bearer = models.User(id=7)
        q = P('id') == 7
        n = bearer.id == 7

        assert evaluate(q, bearer) == n

    def test_evaluate_target_attribute_ne(self):
        bearer = models.User(id=7)
        q = P('id') != 7
        n = bearer.id != 7

        assert evaluate(q, bearer) == n


class TestFilterPredicate(BaseTest):

    def setup(self):
        super(TestFilterPredicate, self).setup()

        # Add 6 users, 2 teams, and link the first 3 to 1 and the
        # second 3 to 2.

        self.users = users = []
        for n in range(6):
            users.append(models.User(name=str(n)))

        self.session.add_all(users)
        self.session.commit()

        teams = []
        for n in range(2):
            teams.append(models.Team(name=str(n)))

        self.session.add_all(teams)
        self.session.commit()

        links = []
        for n in range(3):
            links.append(models.Membership(team=teams[0], user=users[n],
                                           is_active=True))

        for n in range(3):
            links.append(models.Membership(team=teams[1], user=users[n + 3],
                                           is_active=False))

        self.session.add_all(links)
        self.session.commit()

        # Create 10 boxes (5 for each team).
        self.boxes = boxes = []
        for n in range(5):
            boxes.append(models.Box(team=teams[0]))

        for n in range(5):
            boxes.append(models.Box(team=teams[1]))

        self.session.add_all(boxes)
        self.session.commit()

    def test_eval_filter(self):
        bearer1 = self.users[0]
        bearer2 = self.users[3]

        # Every team in which there is an active membership with.
        q1 = P(bearer1, 'teams', Membership__is_active=True)
        q2 = P(bearer2, 'teams', Membership__is_active=True)

        assert len(evaluate(q1).all()) == 1
        assert len(evaluate(q2).all()) == 0

    def test_box_check(self):
        bearer1 = self.users[0]
        bearer2 = self.users[3]

        # Every team in which there is an active membership with.
        x1 = P(bearer1, 'teams', Membership__is_active=True)
        x2 = P(bearer2, 'teams', Membership__is_active=True)

        # Every box that belongs to that team.
        q1 = P('team').in_(x1)
        q2 = P('team').in_(x2)

        assert evaluate(q1, self.boxes[0])
        assert evaluate(q1, self.boxes[3])
        assert not evaluate(q1, self.boxes[7])
        assert not evaluate(q2, self.boxes[6])
        assert not evaluate(q2, self.boxes[8])
        assert not evaluate(q2, self.boxes[7])

    def test_box_filter(self):
        bearer1 = self.users[0]
        bearer2 = self.users[3]

        # Every team in which there is an active membership with.
        x1 = P(bearer1, 'teams', Membership__is_active=True)
        x2 = P(bearer2, 'teams', Membership__is_active=True)

        # Every box that belongs to that team.
        q1 = P('team').in_(x1)
        q2 = P('team').in_(x2)

        E = lambda x: evaluate(x, models.Box)
        assert self.session.query(models.Box).filter(E(q1)).count() == 5
        assert self.session.query(models.Box).filter(E(q2)).count() == 0
