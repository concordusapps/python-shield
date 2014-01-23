# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):

    __tablename__ = 'user'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

    name = sa.Column(sa.Unicode(250), default='', nullable=False)

    teams = orm.relationship(
        'Team',
        backref=orm.backref('users', lazy='dynamic'),
        lazy='dynamic',
        secondary=lambda: Membership.__table__,
        foreign_keys=lambda: [Membership.team_id, Membership.user_id])


class Team(Base):

    __tablename__ = 'team'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

    name = sa.Column(sa.Unicode(250), default='', nullable=False)


class Membership(Base):

    __tablename__ = 'membership'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

    user_id = sa.Column(sa.ForeignKey(User.id), nullable=False)

    user = orm.relationship(User)

    team_id = sa.Column(sa.ForeignKey(Team.id), nullable=False)

    team = orm.relationship(Team)

    is_active = sa.Column(sa.Boolean, nullable=False)


class Box(Base):

    __tablename__ = 'box'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

    team_id = sa.Column(sa.ForeignKey(Team.id), nullable=False)

    team = orm.relationship(Team)


engine = sa.create_engine('sqlite:///:memory:')

Session = orm.sessionmaker(bind=engine)
