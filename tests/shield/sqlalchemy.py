# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):

    __tablename__ = 'user'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)


class Book(Base):

    __tablename__ = 'book'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

    owner_id = sa.Column(sa.Integer, sa.ForeignKey(User.id))


class Color(Base):

    __tablename__ = 'color'

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

    book_id = sa.Column(sa.Integer, sa.ForeignKey(Book.id))

    book = orm.relationship(Book, backref='colors')

    name = sa.Column(sa.Unicode(1024))


engine = sa.create_engine('sqlite:///:memory:')

Session = orm.sessionmaker(bind=engine)
