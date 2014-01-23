# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import pytest
import shield
from . import sqlalchemy as models
from . import test_rule


class BaseTest:

    @pytest.fixture(autouse=True, scope='function')
    def database(self, request):
        meta = models.Base.metadata
        meta.create_all(models.engine)
        request.addfinalizer(lambda: meta.drop_all(models.engine))

    def setup(self):
        self.session = models.Session()


class TestBearer(BaseTest, test_rule.BaseTestBearer):

    Bearer = models.User

    @classmethod
    def setup_class(cls):
        # Declare rules to test with.
        @shield.rule('luck', bearer=cls.Bearer)
        def user_has_luck(bearer):
            # Users are lucky if there ID is 7.
            return bearer.id == 7

    def setup(self):
        super(TestBearer, self).setup()

        # Add 49 users (so 7 of them are lucky).
        for n in range(49):
            self.session.add(models.User())
            self.session.commit()

    def test_bearer_filter(self):
        clause = shield.filter('luck', bearer=self.Bearer)
        items = self.session.query(self.Bearer).filter(clause).all()

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

    def setup(self):
        super(TestTarget, self).setup()

        # Add 7 users and 7 books for each user.
        for x in range(7):
            user = models.User()

            self.session.add(user)
            self.session.commit()

            for y in range(7):
                self.session.add(models.Book(owner_id=user.id))

            self.session.commit()

    def test_bearer_target_filter(self):
        u = models.User(id=7)
        clause = shield.filter('read', bearer=u, target=models.Book)
        items = self.session.query(models.Book).filter(clause).all()

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
            clause = clause and any(c.name in colors for c in target.colors)
            return clause

        @user_can_read_book.expression
        def user_can_read_book(target, bearer):
            # User can read the book if they own the book.
            clause = target.owner_id == bearer.id

            # Futhermore the book must be red or brown.
            clrs = ['red', 'brown']
            clause = clause & target.colors.any(models.Color.name.in_(clrs))
            return clause

    def setup(self):
        super(TestTargetExpression, self).setup()

        # Add 7 users and 7 books for each user.
        colors = ['red', 'brown', 'green', 'blue', 'black', 'white', 'pink']
        for x in range(7):
            user = models.User()

            self.session.add(user)
            self.session.commit()

            for y in range(7):
                book = models.Book(owner_id=user.id)

                self.session.add(book)
                self.session.commit()

                # Futermore, add a color based on the index.
                color = models.Color(book=book, name=colors[y])

                self.session.add(color)
                self.session.commit()

    def test_bearer_target_expression_filter(self):
        u = models.User(id=7)
        clause = shield.filter('read', bearer=u, target=models.Book)
        items = self.session.query(models.Book).filter(clause).all()

        assert len(items) == 2

    def test_bearer_target_expression_has(self):
        u = self.Bearer(id=7)
        b = self.Book(owner_id=7)
        c = self.Color(book=b, name='red')
        b.color_set = [c]

        assert shield.has('read', bearer=u, target=b)
