# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division
import pytest
import models
import shield


class BaseTest(object):

    @pytest.fixture(autouse=True, scope='function')
    def database(self, request):
        meta = models.Base.metadata
        meta.create_all(models.engine)
        request.addfinalizer(lambda: meta.drop_all(models.engine))

    def setup(self):
        self.session = models.Session()


class TestBearer(BaseTest):

    @classmethod
    def setup_class(cls):
        # Declare rules to test with.
        @shield.rule('luck', bearer=models.User)
        def user_has_luck(bearer):
            # Users are lucky if there ID is divisible by 7.
            return bearer.id % 7 == 0

    def setup(self):
        super(TestBearer, self).setup()
        # Add 49 users (so 7 of them are lucky).
        for n in range(49):
            self.session.add(models.User())
            self.session.commit()

    def test_bearer_has(self):
        u = models.User(id=7)

        assert shield.has('luck', bearer=u)

    def test_bearer_has_not(self):
        u = models.User(id=6)

        assert not shield.has('luck', bearer=u)

    def test_bearer_has_unknown(self):
        u = models.User(id=7)

        assert not shield.has('luck2', bearer=u)

    def test_bearer_filter(self):
        clause = shield.filter('luck', bearer=models.User)
        items = self.session.query(models.User).filter(clause).all()

        assert len(items) == 7

    def test_bearer_filter_unknown(self):
        clause = shield.filter('luck2', bearer=models.User)
        items = self.session.query(models.User).filter(clause).all()

        assert len(items) == 0


class TestTarget(BaseTest):

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

    def test_bearer_target_has(self):
        u = models.User(id=7)
        b = models.Book(owner_id=7)

        assert shield.has('read', bearer=u, target=b)

    def test_bearer_target_has_not(self):
        u = models.User(id=7)
        b = models.Book(owner_id=3)

        assert not shield.has('read', bearer=u, target=b)

    def test_bearer_target_has_unknown(self):
        u = models.User(id=7)
        b = models.Book(id=63, owner_id=7)

        assert not shield.has('write', bearer=u, target=b)

    def test_bearer_target_filter(self):
        u = models.User(id=7)
        clause = shield.filter('read', bearer=u, target=models.Book)
        items = self.session.query(models.Book).filter(clause).all()

        assert len(items) == 7

    def test_bearer_target_filter_unknown(self):
        u = models.User(id=7)
        clause = shield.filter('luck2', bearer=u, target=models.Book)
        items = self.session.query(models.Book).filter(clause).all()

        assert len(items) == 0


class TestTargetExpression(BaseTest):

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

    def test_bearer_target_expression_has(self):
        u = models.User(id=7)
        b = models.Book(owner_id=7)
        c = models.Color(book=b, name='red')
        b.colors = [c]

        assert shield.has('read', bearer=u, target=b)

    def test_bearer_target_expression_has_not(self):
        u = models.User(id=7)
        b = models.Book(owner_id=7)

        assert not shield.has('read', bearer=u, target=b)

    def test_bearer_target_expression_filter(self):
        u = models.User(id=7)
        clause = shield.filter('read', bearer=u, target=models.Book)
        items = self.session.query(models.Book).filter(clause).all()

        assert len(items) == 2
