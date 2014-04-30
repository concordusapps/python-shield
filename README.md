# shield
[![Build Status](https://travis-ci.org/concordusapps/python-shield.png?branch=master)](https://travis-ci.org/concordusapps/python-shield)
[![Coverage Status](https://coveralls.io/repos/concordusapps/python-shield/badge.png?branch=master)](https://coveralls.io/r/concordusapps/python-shield?branch=master)
[![PyPi Version](https://pypip.in/v/shield/badge.png)](https://pypi.python.org/pypi/scim)
![PyPi Downloads](https://pypip.in/d/shield/badge.png)
> A permissions framework built around declarative rules that is ORM-agnostic.

**Shield** faciltiates the creation of functional rules that define permissions on a *bearer* object optionally in relation to a *target* object. **Shield** is currently designed to work exclusively with sqlalchemy.

## Usage

### Concepts

#### Bearer

A *bearer* is the entity the permission is being granted to.

#### Target

A *target* is the entity the *bearer* is being granted accessed to.

### Rule

A `shield.rule` is a declarative system to register a rule function.  The rule
function recieves a query and performs arbitrary operations in order to return
a more decorated query representing the rule's application.

A `shield.rule` may be registered just on the **bearer** as follows.

```python
@shield.rule('luck', bearer=User)
def user_has_luck(query, bearer, **kwargs):
    # Only users whose id is 7 are lucky.
    return query.filter(bearer.id == 7)

# Check to see if a specific user is lucky.
>>> u = User(id=54)
>>> shield.has('luck', bearer=u)
False

>>> u.id = 7
>>> shield.has('luck', bearer=u)
True

# Retrieve all users who are lucky.
>>> query = shield.filter('luck', bearer=u)
>>> query.all()
[<User(id=7)>]
```

A `shield.rule` may be further constrained to correspond to a **target** as
follows.

```python
@shield.rule('read', bearer=User, target=Book)
def can_user_read_book(query, target, bearer, **kwargs):
    # A user may read a book if it is its owner
    return query.filter(target.owner_id == bearer.id)

# Check if a specific user can read a specific book.
>>> u = User(id=32)
>>> b = Book(owner_id=32)
>>> shield.has('read', bearer=u, target=b)
True

# Retrieve all books that a specific user can read.
>>> u = User(id=10)
>>> query = shield.filter('read', bearer=u, target=Book)
>>> query.all()
[<Book(owner=User(id=10))>, <Book(owner=User(id=10))>, <Book(owner=User(id=10))>]
```

### Deferred rules

With a complicated rules system, many rules may be defined in terms of other
rules.  Shield provides a shortcut in the case of a rule being defined
completely in terms of another rule.

```python
# Create a rule for books that can be read.
@shield.rule('read', bearer=User, target=Book)
def can_user_read_book(query, target, bearer, **kwargs):
    # Users can only read the book if the book's color is red
    return query.filter(target.color == 'red')

# The rules for a book also apply to the book's pages.
shield.deferred_rule(attributes=('book',), bearer=User, target=Page)


>>> u = User(id=10)
>>> query = shield.filter('read', bearer=u, target=Book)
>>> query.all()
[<Book(id=2, owner=User(id=10), color='red')>]

# Now fetch the pages that the user can read.
>>> query = shield.filter('read', bearer=u, target=Book)
>>> query.all()
[<Page(book_id=2, pagenum=1)>, <Page(book_id=2, pagenum=2)>, <Page(book_id=2, pagenum=3)>]
```

### API

#### shield.rule decorator

The rule decorator has the following signature:
`shield.rule(*permissions, target, bearer)`
 * `*permissions` (optional): an arbitrary permission type representing the
   kind of permission being defined for this function.  In the examples, this
   was a string; however, this can be any kind of hashable type.

 * `target` (optional): A class object representing the object the bearer has
   permission on.

 * `bearer`: A class object represetning the type of object the bearer is.

Rules are defined in the following manner when arguments above are missing:
 * No arguments missing: `bearer` HAS permissions ON `target`
 * `target` missing: `bearer` HAS permissions
 * `permissions` missing: `bearer` HAS ALL PERMISSIONS ON `target`

#### shield.rule decoration

The rule function should have the following signature.  Note that all arguments
are invoked as keyword arguments:
```python
def rule(query, bearer, target, permission):
    return query
```
 * `query`: A sqlalchemy query object that should be used as a base for
   filtering.  This query is scoped to the target class, such that it is
   equivelent to `session.query(target)`.  Note that in the case of a rule
   function being called as the result of a deferred rule, the query is
   equivelent to
   `session.query(deferrer).join(deferree, getattr(deferrer, attribute))`
 * `bearer`: The class object representing the bearer for querying.
 * `target`: The class object representing the target for querying.  Note that
   in the case of deferred rules, the target object is an aliased class (so
   that rules defined for adjacency lists work nicely.)
 * 'permission': the permission currently being checked.

#### shield.filter and shield.has

`shield.filter` has the following signature:
`sheild.filter(*permissions, bearer, target, query, session)`
 * `*permissions` (optional): The permissions being tested on the target
 * `bearer`: An instance of the bearer class
 * `target`: The target class object.
 * `query` (optional): the query object that will be passed to the rules.
 * `session` (optional): The session object used to create a query for each
   rule

`shield.has` has the same function signatuer as `shield.filter`, except
`target` should be an instance of the target class, not the class object.
Shield will first attempt to use the provided query when invoking rules.  If no
query was provided, it will attempt to make one using the provided session
object.  If no session object was provided, shield will attempt to use the
session object associated with the bearer.

## License
Unless otherwise noted, all files contained within this project are liensed under the MIT opensource license. See the included file LICENSE or visit [opensource.org][] for more information.

[opensource.org]: http://opensource.org/licenses/MIT
