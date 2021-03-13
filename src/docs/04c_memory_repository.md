# 4. First Use Case

## 4c. In-Memory UserRepository Implementation

To illustrate the basics of the repository we will first implement a variation that keeps all data in memory. We can do this with basic Python objects and don't have to worry about the underlying details of the storage medium. An in-memory implementation will also be useful for testing because we don't have to set up external dependencies like a database.

While the memory implementation has no external dependencies, we want to pass in the configuration from our AppDependencies. We can then use the configuration to load test data (_fixtures_) when the repository is created.

The skeleton of our `MemoryUserRepository` should look like this:

```python
# app/adapters/repositories/users/memory_user_repository.py
from typing import List, Optional

from app.domain.users.entities import User
from app.domain.users.interfaces import UserRepositoryInterface

class MemoryUserRepository(UserRepositoryInterface):
     """in-memory implementation of UserRepository"""

    def __init__(self, config: dict[str, Any]):
        """set up dict as 'storage' and load fixtures based on config"""
        self._users: dict[str, dict] = {}

        # load test data from fixture file when running tests
        environment = config["environment"]
        fixtures = config["repositories"]["fixtures"]

        if environment == "test" and "users" in fixtures:
            print("\nENV: %s" % environment)
            print(fixtures["users"])

        async def find_all(self) -> List[User]:
            return []

        async def find_users_by_attributes(self, attributes: dict) -> List[User]:
            return []

        async def get_user_by_id(self, id: str) -> Optional[User]:
            return None

        async def get_users_by_ids(self, ids: List[str]) -> List[User]:
            return []

        async def delete_user(self, id: str) -> bool:
            return False

        async def save_new_user(self, user: User) -> User:
            return user

        async def update_user(self, user: User) -> User:
            return user
```

> The class is a subclass of `UserRepositoryInterface` which requires it to implement stubs for all methods that are defined by the interface. Without this we would get errors when running our tests.

For now let's just focus on the `__init__` method. We have defined one argument called `config` which is of type `dict[str, Any]`. At runtime the DI framework will inject the _value_ of the `AppDependencies.config` provider which is a nested `dict` object. The shape and default values of this nested dict is set up in `config.py` and critical values are overwritten in `di_containers.py` and `conftest.py` from the environment variables.

As storage we use a plain Python dictionary that maps the user's id to the the user data object (also a Python dictionary). The interface does not define how the data is stored. The only requirement is that we convert the raw data to a `User` object when we return it.

### Setting up the Test environment

For testing we already have overwritten the `environment` config setting to 'test'. Now we need to add a value for the fixtures path.

```python
# tests/conftest.py
fixtures = {
    "users": "tests/fixtures/users.json",
}

@pytest.fixture(scope="session")
def dependencies():
    dependencies = AppDependencies()
    dependencies.init_resources()

    # overwrite the fixtures setting
    dependencies.config.repositories.fixtures.from_dict(fixtures)

    # TODO: dependency discovery

    yield dependencies
```

Note that we still haven't enabled the dependencies discovery. In the unit tests we will create instances of the _MemoryUserRepository_ outside of the DI framework so the framework does not have to be aware of those instances. We will have to provide the configuration from the `dependencies` instance to the constructor, though.

The `dependencies.config` container is a tree of _Providers_ that can be accessed as attributes of their parent node (see the `dependencies.config.repositories.fixtures` example above). If we want to get the value, we can invoke the `config` node directly which will return a nested dict with the current configuration. We can define another Pytest fixture to provide this object consistently to all tests.

```
@pytest.fixture(scope="session")
def config(dependencies):
    yield dependencies.config()
```

Now we add our first test case to confirm that the configuration is applied properly. Our requirement is this:

- **REPO-US-MEM-01:** memory repository instance requires a configuration object

```python
# tests/unit/adapters/repositories/users/test_memory_user_repository.py
from app.adapters.repositories.users.memory_user_repository import MemoryUserRepository

class TestMemoryUserRepository:
    """adapters.repositories.memory_user_repository"""

    def test_memory_user_repository_instance(self, config, capsys):
        """[REPO-US-MEM-01] memory repository requires a configuration object"""
        with capsys.disabled():
            repo = MemoryUserRepository(config)

            assert len(repo._users) == 0
```

I have added a temporary `capsys.disabled` to the test to show the output of the print statements. At its core the test checks that a new instance of the `MemoryUserRepository` class can be created and that it contains no users. When we run the test we should see the following output:

```
(venv) ➜ python -m pytest -k memory_user_repository
======================== test session starts ==========================
platform darwin -- Python 3.9.1, pytest-6.2.0, py-1.10.0, pluggy-0.13.1
rootdir: /Users/thomas/Projects/clean-architecture-python/src, configfile: pytest.ini
collected 12 items / 11 deselected / 1 selected

[REPO-US-MEM-01] adapters.repositories.memory_user_repository - memory repository instance requires a configuration object
ENV: test
tests/fixtures/users.json
.                                                                [100%]
============ 1 passed, 11 deselected, 2 warnings in 0.06s =============
```

The two lines just under the test name show the output of our print statement. We see that the environment is set to `test` and the the path for the user fixtures is set to `tests/fixtures/user.json`. These are the values we defined in `dependencies.config` in the `conftest.py` file.

### Loading fixtures

The fixture we are going to load are in JSON format in the file `tests/fixtures/users.json`. It's a list of JSON objects with the user data that our User entity requires (plus a `password_hash` that we will need later for authentication). Here is an example:

```JSON
[
  {
    "id": "USER-ADM",
    "email": "admin@example.com",
    "first_name": "Admin",
    "is_admin": true,
    "organization_id": "",
    "last_name": "SysAdmin",
    "password_hash": "$2b$12$/bxSAKp5FLBWOs/zq4n8xOmoR2hlXaEQ/60I58xTfKpbYSQOF7N0i"
  },
  ...
]
```

Here is a simple utility to load the raw data from the JSON file:

```python
# app/adapters/repositories/utils.py
import os
import json
from typing import List

def load_fixtures(fixtures_path: str) -> List[dict[str, str]]:
    if not os.path.exists(fixtures_path):
        return []

    try:
        with open(fixtures_path) as fixtures_file:
            data = json.load(fixtures_file)
            return data
    except:
        return []
```

We can update our `__init__` method to use this function instead of printing the config values:

```python
# app/adapters/repositories/users/memory_user_repository.py
...
from ..utils import load_fixtures

...
        # load test data from fixture file when running tests
        if environment == "test" and "users" in fixtures:
            data = load_fixtures(fixtures["users"])
            self._users = {user["id"]: user for user in data}
```

Now we can remove the `capsys.disable()` call in the test file and update the assertion to expect the number of users that are set up in our fixtures file. If we just hard-code the number we create a brittle test that we have to update every time we change our test data. Instead we can set up another pytest fixture with the same logic as the `__init__` method to load the data from the file:

```python
# tests/conftest.py
...
from app.adapters.repositories.utils import load_fixtures
...

@pytest.fixture(scope="session")
def all_users():
    data = load_fixtures(fixtures["users"])
    yield data
```

Now the new fixture gives us access to the user data in our repo:

```python
# tests/unit/adapters/repositories/users/test_memory_user_repository.py
...
    def test_memory_user_repository_instance(self, config, all_users):
        """[REPO-US-MEM-01] memory repository instance requires a configuration object"""
        repo = MemoryUserRepository(config)

        assert len(repo._users) == len(all_users)
```

Rerun the test to confirm that it passes again.

### Testing non-test environments

The automatic loading of fixtures also has a flip side: If we are not in the 'test' or we do not provide a fixture path then the repository should start out empty.

- **REPO-US-MEM-02:** memory repository does only load fixtures in test environment
- **REPO-US-MEM-03:** memory repository does not load fixtures without fixture path

Testing this follows the same logic. We create a nested `config` dict but set the `environment` to a string other than `test`. We also have to set the fixture path because we don't want a missing path to affect the outcome of our test.

```python
    def test_memory_user_repository_non_test_env(self):
        """[REPO-US-MEM-02] memory repository does only load fixtures in test environment"""
        config_not_test_env = {
            "environment": "not_test",
            "repositories": {
                "fixtures": {
                    "users": "tests/fixtures/users.json",
                }
            },
        }
        repo = MemoryUserRepository(config_not_test_env)

        assert len(repo._users) == 0
```

Likewise we can remove the fixture path but keep the environment set to `test`:

```python
    def test_memory_user_repository_without_fixture_path(self):
        """[REPO-US-MEM-03] memory repository does not load fixtures without fixture path"""
        config_no_fixture_path = {
            "environment": "test",
            "repositories": {"fixtures": {}},
        }
        repo = MemoryUserRepository(config_no_fixture_path)

        assert len(repo._users) == 0
```

### Listing all users

We can now implement and test the methods of our repository. A simple case is the listing of all existing users. We can split this into two requirements, one formal and one logical:

- **REPO-US-MEM-11:** repository.find*all() returns a \_list* of _User_ entities
- **REPO-US-MEM-12:** repository.find*all() returns \_all* users

For the first test we simply get the result of `find_all()` and check it's type (a list) and the type of the elements (User). But there is a small issue: `find_all` is an async function, so we need to test it in an async test function where we can `await` the result before we make any assertions. Pytest does not support async test function out of the box and will simply skip them. We can add the necessary support by installing a plugin:

```
(venv) $ pip install pytest-asyncio
(venv) $ pip freeze > requirements.txt
```

Then we just have add a decorator to async test itself:

```python
import pytest
from app.domain.users.entities import User
...
    @pytest.mark.asyncio
    async def test_memory_user_repository_find_all_returns_list_of_users(
        self, config
    ):
        """[REPO-US-MEM-11] repo.find_all returns a list of User entities"""
        repo = MemoryUserRepository(config)
        repo_users = await repo.find_all()

        assert isinstance(repo_users, list)
        assert isinstance(repo_users[0], User)
```

Running this test will fail. Or rather, the first assertion will pass and the second will fail. The reason is simple: We still have our stub implementation that returns an empty list. Let's update this with the right implementation:

```python
# app/adapters/repositories/users/memory_user_repository.py
...
    async def find_all(self) -> List[User]:
        """return a list of all users"""
        return [User(**user) for user in self._users.values()]
```

Now we use our actual test data which is pre-populated with the users from our fixture file. The test can access the first element of the result and confirm its type name.

You will notice that there is little error checking. Except for the fixtures which are loaded during `__init__` the only way to create new data is via the `save_new_user` method which take a user as argument. Therefore we can be sure that all data in the repository represents a valid user. If there is an error because of invalid _fixture_ data we can happily let the error surface unmodified. Fixtures are only used for testing where we can see the error and fix the data immediately.

Finally we can add a test to check that the right number of users are returned:

```python
    @pytest.mark.asyncio
    async def test_memory_user_repository_find_all_returns_all_users(
        self, config, all_users
    ):
        """[REPO-US-MEM-12] repo.find_all returns all users"""
        repo = MemoryUserRepository(config)
        repo_users = await repo.find_all()

        assert len(repo_users) == len(all_users)
```

### Get single user by id

With the `find_all` method as template we can quickly set up tests for the `get_user_by_id` method:

```python
    @pytest.mark.asyncio
    async def test_memory_user_repository_get_user_by_id_returns_users(
        self, config, all_users
    ):
        """[REPO-US-MEM-21] repo.get_user_by_id returns a User"""
        repo = MemoryUserRepository(config)
        user = await repo.get_user_by_id(all_users[0]["id"])

        assert user is not None
        assert isinstance(user, User)
        assert user.id == all_users[0]["id"]

    @pytest.mark.asyncio
    async def test_memory_user_repository_get_user_by_id_returns_none(
        self, config
    ):
        """[REPO-US-MEM-22] repo.get_user_by_id returns all users"""
        repo = MemoryUserRepository(config)
        user = await repo.get_user_by_id("no-such-id")

        assert user is None
```

And the implementation of the method is again very concise:

```python
    async def get_user_by_id(self, id: str) -> Optional[User]:
        return User(**self._users[id]) if id in self._users else None
```

Adding and testing the `get_users_by_ids` method is now almost trivial. See the Github repository for details.

### Find users by attributes

The `find_users_by_attributes` method returns a subset of users with given attribute values. This is the equivalent of a SQL `SELECT ... WHERE ...` statement. For our memory storage based on Python dictionaries we can define a helper function that loops through the filter criteria (provided as dict) and selects those data sets that match the current attribute value.

```python
# app/adapters/repositories/utils.py

def filter_entities_by_attributes(data: dict[str, dict], attributes: dict[str, Any]):
    _set = dict[str, dict]

    for key, value in attributes.items():
        _set = [entity for entity in _set if entity[key] == value]

    return _set
```

With the helper function the implementation of the method is again straight forward: We first get the list of matching user data entries, then we convert them to User objects and return the resulting list.

```python
    async def find_users_by_attributes(self, attributes: dict) -> List[User]:
        """return list of users with given attribute values"""
        users = filter_entities_by_attributes(self._users, attributes)
        return [User(**user) for user in users]
```

### Creating a new user

When we create a new user we will receive the (almost complete) user data as a `NewUserDTO` entity. We have to generate an `id` as our primary identifier that does not conflict with another user's id. Then we can just add the record to our storage and return a new `User` entity from the data.

```python
    async def save_new_user(self, data: NewUserDTO) -> User:
        """create new record and return user"""
        id = str(uuid4())
        while id in self._users:
            id = str(uuid4())

        user = {**data.dict(), "id": id}
        self._users[id] = user

        return User(**user)
```

### Updating an existing user

Our update function is quite simple. We only need to update the existing data record and write it back to storage. The only complication could be that the user we want to update does not exist. We have to treat this as an error case because we have no other option to indicate that no update has taken place.

```python
    async def update_user(self, user: User) -> User:
        """update an existing user in storage"""
        if user.id not in self._users:
            raise ValueError(f"User with id {user.id} does not exist.")

        self._users[user.id] = {**self._users[user.id], **user.dict()}

        return user
```

### Deleting a user

The `delete_user` method of the repository will remove all user data from storage. The repository does not know about any dependencies that related data might have on the user. It is up to the logic level to remove dependent data before the user is deleted.

Again we treat an id that does not exist as an error. Returning `False` would be ambiguous in this case. In fact, we expect this method only to return `True` as a successful status and raise exceptions in any other case.

```python
    async def delete_user(self, id: str) -> bool:
        """delete a user from storage"""
        if id not in self._users:
            raise ValueError(f"User with id {id} does not exist.")

        del self._users[id]

        return True
```

### Summary

With that we have implemented our complete interface. All our methods only require a few lines of code. This is mostly due to the limited features that each method provides. On their own these basic operations are not enough to support a complex programme. But with additional layers for service and use cases we can implement complex logic requirements based of very simple operations.

Each of the levels implements a specific aspect so that higher level functions do not have to deal with the details. In turn, the higher level functions can be reduced to simple logical steps. All this keeps our code maintainable when the number and complexity of features increases over time.
