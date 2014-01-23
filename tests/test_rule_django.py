# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import pytest
import shield
from django.db.models import Q
from . import models
from . import test_rule


class BaseTest:

    @pytest.fixture(autouse=True, scope='function')
    def database(self, request):
        # Initialize the database and create all models.
        from django.db import connections, DEFAULT_DB_ALIAS
        connection = connections[DEFAULT_DB_ALIAS]
        name = connection.creation.create_test_db(verbosity=0)
        destroy = connection.creation.destroy_test_db
        request.addfinalizer(lambda: destroy(name, verbosity=0))


class TestBearer(BaseTest, test_rule.BaseTestBearer):

    Bearer = models.User

    @classmethod
    def setup_class(cls):
        # Declare rules to test with.
        @shield.rule('luck', bearer=cls.Bearer)
        def user_has_luck(bearer):
            return bearer.id == 7

        @user_has_luck.expression
        def user_has_luck(bearer):
            return Q(id=7)

    def setup(self):
        for n in range(10):
            models.User(username=str(n)).save()

    def test_bearer_filter(self):
        clause = shield.filter('luck', bearer=self.Bearer)
        items = self.Bearer.objects.filter(clause).all()

        assert len(items) == 1


class TestTarget(BaseTest, test_rule.BaseTestBearer):

    Bearer = models.User

    Target = models.Book

    @classmethod
    def setup_class(cls):
        # Declare rules to test with.
        @shield.rule('read', bearer=models.User, target=models.Book)
        def user_can_read_book(target, bearer):
            # User can read the book if they own the book.
            return target.owner_id == bearer.id

        @user_can_read_book.expression
        def user_can_read_book(target, bearer):
            # User can read the book if they own the book.
            return Q(owner_id=bearer.id)

    def setup(self):
        # Add 7 users and 7 books for each user.
        for x in range(7):
            user = models.User(username=str(x))
            user.save()

            for y in range(7):
                models.Book.objects.create(owner=user)

    def test_bearer_target_filter(self):
        u = models.User(id=7)
        clause = shield.filter('read', bearer=u, target=models.Book)
        items = models.Book.objects.filter(clause).all()

        assert len(items) == 7


class TestTargetExpression(BaseTest, test_rule.BaseTestTargetExpression):

    Bearer = models.User

    Book = models.Book

    Color = models.Color

    @classmethod
    def setup_class(cls):
        # Declare rules to test with.
        @shield.rule('read', bearer=models.User, target=models.Book)
        def user_can_read_book(target, bearer):
            # User can read the book if they own the book.
            clause = target.owner_id == bearer.id

            # Futhermore the book must be red or brown.
            colors = ['red', 'brown']
            color_set = target.color_set.all()
            clause = clause and any(c.name in colors for c in color_set)
            return clause

        @user_can_read_book.expression
        def user_can_read_book(target, bearer):
            # User can read the book if they own the book.
            clause = Q(owner_id=bearer.id)

            # Futhermore the book must be red or brown.
            clrs = ['red', 'brown']
            clause &= Q(color__name__in=clrs)
            return clause

    def setup(self):
        # Add 7 users and 7 books for each user.
        colors = ['red', 'brown', 'green', 'blue', 'black', 'white', 'pink']
        for x in range(7):
            user = models.User(username=str(x))
            user.save()

            for y in range(7):
                book = models.Book.objects.create(owner=user)

                # Futermore, add a color based on the index.
                color = models.Color(book=book, name=colors[y])
                color.save()

    def test_bearer_target_expression_has(self):
        u = self.Bearer(id=7)
        u.save()
        b = self.Book(owner_id=7)
        b.save()
        c = self.Color(book=b, name='red')
        c.save()

        assert shield.has('read', bearer=u, target=b)

    def test_bearer_target_expression_filter(self):
        u = models.User(id=7)
        clause = shield.filter('read', bearer=u, target=models.Book)
        items = models.Book.objects.filter(clause).all()

        assert len(items) == 2
