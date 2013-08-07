# shield
[![Build Status](https://travis-ci.org/concordusapps/python-shield.png?branch=master)](https://travis-ci.org/concordusapps/python-shield)
[![Coverage Status](https://coveralls.io/repos/concordusapps/python-shield/badge.png?branch=master)](https://coveralls.io/r/concordusapps/python-shield?branch=master)
[![PyPi Version](https://pypip.in/v/shield/badge.png)](https://pypi.python.org/pypi/scim)
![PyPi Downloads](https://pypip.in/d/shield/badge.png)
> A permissions framework built around declarative rules that is ORM-agnostic.

**Shield** faciltiates the creation of functional rules that define permissions on a *bearer* object optionally in relation to a *target* object. **Sheild** should work in most ORMs and has a test suite for usage in *django* and *sqlalchemy*.

## Usage

### Concepts

#### Bearer

A *bearer* is the entity the permission is being granted to.

#### Target

A *target* is the entity the *bearer* is being granted accessed to.

### Rule

A `shield.rule` is a declarative system to register a query expression that must match for the given **bearer** in order for the permission to be granted.

A `shield.rule` may be registered just on the **bearer** as follows.

```python
@shield.rule('luck', bearer=User)
def user_has_luck(bearer):
    # Only users whose id is 7 are lucky.
    return bearer.id == 7

# Check to see if a specific user is lucky.
>>> u = User(id=54)
>>> shield.has('luck', bearer=u)
False

>>> u.id = 7
>>> shield.has('luck', bearer=u)
True

# Retrieve all users who are lucky.
>>> clause = shield.filter('luck', bearer=u)
>>> session.query(User).filter(clause).all()
[{...}]
```

A `shield.rule` may be further registered to correspond to a **target** as follows.

```python
@shield.rule('read', bearer=User, target=Book)
def can_user_read_book(target, bearer):
    # A user may read a book if it is its owner
    return target.owner_id == bearer.id

# Check if a specific user can read a specific book.
>>> u = User(id=32)
>>> b = Book(owner_id=32)
>>> shield.has('read', bearer=u, target=b)
True

# Retrieve all books that a specific user can read.
>>> u = User(id=10)
>>> clause = shield.filter('read', bearer=u, target=Book)
>>> session.query(Book).filter(clause).all()
[{...}, {...}, {...}]
```

### Expression

With advanced rules or limited ORMs, the desired query may not be able
to be expressed in a way that works with both filtering and functionally checking.

```python
@shield.rule('read', bearer=User, target=Book)
def can_user_read_book(target, bearer):
    # Users can only read the book if the books colors are in a set.
    return target.color in {'red', 'blue', 'gold'}

@can_user_read_book.expression
def can_user_read_book(target, bearer):
    # Users can only read the book if the books colors are in a set.
    return target.color.in_({'red', 'blue', 'gold'})
```

In other ORMs besides SQLAlchemy (such as django), you will likely need to
provide a conditional rule and an expression rule for each permission set
you would like to have.

## License
Unless otherwise noted, all files contained within this project are liensed under the MIT opensource license. See the included file LICENSE or visit [opensource.org][] for more information.

[opensource.org]: http://opensource.org/licenses/MIT
