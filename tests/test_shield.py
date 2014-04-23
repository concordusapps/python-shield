# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import pytest
import shield
from . import sqlalchemy as models


class BaseTest(object):

    @pytest.fixture(autouse=True, scope='function')
    def database(self, request):
        meta = models.Base.metadata
        meta.create_all(models.engine)
        request.addfinalizer(lambda: meta.drop_all(models.engine))

    def setup(self):
        self.session = models.Session()


class RuleTest(BaseTest):

    @pytest.fixture(autouse=True, scope='function')
    def register_rules(self, request):
        request.addfinalizer(lambda: shield.registry.clear())


class FixtureTest(BaseTest):
    def setup(self):
        super(FixtureTest, self).setup()
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


class TestRegistry(RuleTest, FixtureTest):

    def rule(self, **kwargs):
        return 'invoked'

    def register_specific_rule(self):
        rule = shield.rule('member', bearer=models.User, target=models.Team)
        rule(self.rule)

    def register_target_rule(self):
        shield.rule(bearer=models.User, target=models.Team)(self.rule)

    def register_bearer_rule(self):
        shield.rule('member', bearer=models.User)(self.rule)

    def test_register_normal_rule(self):
        self.register_specific_rule()

        assert len(shield.registry) == 1

    def test_register_target_rule(self):

        self.register_target_rule()

        assert len(shield.registry) == 0
        assert len(shield.registry.target) == 1

    def test_register_bearer_rule(self):
        self.register_bearer_rule()

        assert len(shield.registry) == 0
        assert len(shield.registry.bearer) == 1

    def test_retrieve_existing_rules(self):
        self.register_specific_rule()
        self.register_target_rule()
        self.register_bearer_rule()

        rules = []

        # BEARER has PERMISSION on TARGET
        rules.append(shield.registry.retrieve(
            permission='member',
            bearer=models.User,
            target=models.Team))

        # BEARER has all permissions on TARGET
        rules.append(shield.registry.retrieve(
            bearer=models.User,
            target=models.Team))

        # BEARER has PERMISSION
        rules.append(shield.registry.retrieve(
            permission='member',
            bearer=models.User))

        for rule in rules:
            assert rule is not None
            assert rule() == 'invoked'

    def test_retrieve_nonexistant_rule(self):
        self.register_specific_rule()

        # Generate argument calls for the registry retrieval
        args = [

            # BEARER has PERMISSION on TARGET
            {
                'permission': 'awesome',  # invalid.
                'bearer': models.User,
                'target': models.Team,
            },
            # BEARER has all permissions on TARGET
            {
                'bearer': models.Box,  # invalid.
                'target': models.Team,
            },
            # BEARER has PERMISSION
            {
                'permission': 'awesome',  # invalid.
                'bearer': models.User,
            }
        ]

        for argset in args:
            with pytest.raises(KeyError):
                shield.registry.retrieve(**argset)

    def test_inherited_caching(self):
        self.register_target_rule()

        assert len(shield.registry.target) == 1

        shield.registry.retrieve(
            bearer=models.User,
            target=models.DerivedTeam)

        assert len(shield.registry.target) == 2

    def test_no_caching(self):

        shield.rule(
            target=models.Team,
            bearer=models.User,
            cache=False)(self.rule)

        assert len(shield.registry.target) == 1

        shield.registry.retrieve(target=models.Team, bearer=models.User)

        assert len(shield.registry.target) == 1


class TestInterface(RuleTest, FixtureTest):
    """Test common interfaces (shield.filter and shield.has)"""

    def register_membership(self):
        @shield.rule('member', bearer=models.User, target=models.Team)
        def user_is_member_of_team(query, bearer, **kwargs):
            # return teams that this user is part of.  query is scoped to team
            return query.join(models.Membership).filter(
                models.Membership.user == bearer)

    def register_deferred(self):
        pass

    def test_filter(self):
        self.register_membership()

        user = self.users[0]

        team_ids = {x.id for x in user.teams}

        query = shield.filter(
            'member',
            bearer=user,
            target=models.Team)

        assert {x.id for x in query} == team_ids

    def test_has(self):
        self.register_membership()

        user = self.users[0]

        result = shield.has(
            'member',
            bearer=user,
            target=user.teams.first())

        assert result is True

    def test_deferred(self):
        self.register_membership()

        shield.deferred_rule(
            'member',
            attributes=('team',),
            bearer=models.User,
            target=models.Box)

        result = shield.filter(
            'member',
            bearer=self.users[0],
            target=models.Box)

        assert result.count() == 5

    def test_deferred_target_style(self):
        self.register_membership()

        shield.deferred_rule(
            attributes=('team',),
            bearer=models.User,
            target=models.Box)

        result = shield.filter(
            'member',
            bearer=self.users[0],
            target=models.Box)

        assert result.count() == 5
