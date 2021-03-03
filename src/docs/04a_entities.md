# 4. First Use Case

## 4a. Entities

In our system data is represented as _entities_. These are simple object that hold a set of attribute values with only a tiny amount of validation logic attached. They transfer data between our repositories, services and use cases.

The only methods an entity needs are those to create a new instance from a basic set of values and to convert the entity back to a basic set of values. The _basic set of values_ is a Python dictionary.

We could use a dictionary directly for our entities but then we would have no guarantee that the data within conforms to our requirements. Python dictionaries provide little type safety so we need to look for other options. Luckily, others have already found a solution for this: [pydantic](https://pydantic-docs.helpmanual.io/).

As the web site says, "_pydantic enforces type hints at runtime, and provides user friendly errors when data is invalid._" That means if we provide the wrong data type (or even values) when we create a new entity pydantic will throw an error and won't let us proceed. If we succeed in creating a new entity we can be sure that the data it contains conforms to our requirements.

As a personal preference I also like to use _immutable_ data structures. _pydantic_ has a solution for this, too.

Let's install _pydantic_ before we continue:

```bash
(venv) $ pip install pydantic
(venv) $ pip freeze > requirements.txt
```

### The User Entity

To define the User entity with _pydantic_ we just need to list the attributes we want and their type. The last two lines make the instance immutable.

```python
# src/app/domain/users/entities.py
from pydantic import BaseModel

class User(BaseModel):
    """representation of a user in our system"""

    id: str
    email: str
    first_name: str
    last_name: str
    organization_id: str
    is_admin: bool

    class Config:
        allow_mutation = False
```

To see how the entity is used and to confirm that it works as expected we can write some unit tests. Let's set up a file with a test suite for the _User_ class and a dictionary with attribute values:

```python
# src/tests/unit/domain/users/test_user_entities.py
import pytest

from app.domain.users.entities import User

user_data = {
    "id": "EX-001",
    "email": "ex1@example.com",
    "first_name": "First",
    "last_name": "Last",
    "organization_id": "Org",
    "is_admin": False,
}


class TestUserEntity:
    """domain.entities.user"""
```

#### Creating a new instance

In the first test we will confirm that we can create a new entity from the dictionary. We set up our values as a dictionary and then create a new User instance from the dictionary by supplying the dictionary entries as keyword arguments to the _User_ constructor:

```python
    def test_user_from_named_arguments(self):
        """[DOM-ENT-US-01] user can be created from named arguments"""
        user = User(**user_data)

        assert user.id == user_data["id"]
        assert user.email == user_data["email"]
```

As validation we just check that the id an email values are the same as in our source data. When we run this test all passes.

#### Instance from dictionary

The _pydantic_ BaseModel also provides a more convenient `.parse_obj()` method to create a new instance. We can test this with basically the same test:

```python
    def test_user_from_dictionary(self):
        """[DOM-ENT-US-02] user can be created from dictionary"""
        user = User.parse_obj(user_data)

        assert user.id == user_data["id"]
        assert user.email == user_data["email"]
```

#### Instance from existing instance

When we want to update a user, we can't just change one of the attributes because we have set them up to be immutable. We have to create a new entity and override the attributes we want to change in the process. To get the values from an existing entity, we can use the `.dict()` method.

Unfortunately we can't just add the new values at the end. We can list each keyword attribute only once. So we have to create a new dictionary inline and convert that into a new entity:

```python
    def test_user_from_existing_user(self):
        """[DOM-ENT-US-03] user can be created from an existing user"""
        user1 = User.parse_obj(user_data)
        user2 = User.parse_obj({**user1.dict(), "id": "EX-002"})

        assert user2.id == "EX-002"
        assert user2.email == user_data["email"]
```

#### Missing constructor arguments

In our _User_ model all arguments are required. If one of the arguments is missing in the input data the constructor will fail.

Note: _Pydantic_ has options to set default values but we have not used them.

```python
    def test_user_from_dict_with_missing_arguments(self):
        """[DOM-ENT-US-04] all arguments are required"""
        data = {**user_data}
        del data["email"]

        with pytest.raises(ValidationError):
            user = User.parse_obj(data)
```

#### Extra constructor arguments are ignored

On the plus side, we can supply extra arguments to the constructor. So if we have for example a database row in a dictionary we don't need to filter out keys that the User model doesn't implement. In our test we add an `extra` key to our user data, create a new User instance and then verify that the additional key is not part of the user data:

```python
    def test_user_from_dict_with_extra_arguments(self):
        """[DOM-ENT-US-05] extra constructor arguments are ignored"""
        data = {**user_data, "extra": "unused value"}
        user = User.parse_obj(data)

        assert user.id == user_data["id"]

        with pytest.raises(KeyError):
            user.dict()["extra"]
```

#### Type safety

To prove that _pydantic_ enforces the correct data types, we can supply a value with an incorrect type and confirm that the constructor call fails. Pydantic will raise a _ValidationError_ in this case so we have to write our test based on the fact that the code will fail.

```python
from pydantic import ValidationError

...

    def test_data_types_are_enforced(self):
        """[DOM-ENT-US-06] argument data types are enforced"""
        with pytest.raises(ValidationError):
            user = User(**{**user_data, "is_admin": "not_bool"})
```

#### Immutability

Finally we can test that an instance can not be modified once it has been created:

```python
    def test_user_instance_is_immutable(self):
        """[DOM-ENT-US-07] user instance is immutable"""
        user = User(**user_data)

        with pytest.raises(TypeError):
            user.id = "EX-002"
```
