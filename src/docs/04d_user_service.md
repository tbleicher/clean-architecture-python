# 4. First Use Case

## 4d. UserService

The _UserRepository_ provides us with basic access to the entities. To keep the repository independent from the storage technology we have limited the repository methods to a reasonable minimum. However, for our use cases it would be convenient to have a more feature-rich data access layer, so the use cases can focus on the logic.

For these extra features we can add a new layer of abstraction between the repository and the use cases: the service layer. Here we can add entity access function that are frequently used but go beyond the basic storage handling of the repository.

### UserServiceInterface

The use cases will request data exclusively from the new service layer. If we want to have any of the repository methods available for use cases, we need to expose them in the service. We want to expose all of our repository methods. To create a corresponding interface definition, we can just subclass the `UserRepositoryInterface` to include all methods defined there.

```python
# app/domain/users/interfaces.py

class UserServiceInterface(UserRepositoryInterface):
    """definition of the UserService interface"""
```

#### Adding uniqueness constraints for email

We will use the UserService to add an additional constraint to our data: A user's email address should be unique.

We can use the existing `save_new_user` method definition. Nothing has to change for the interface, we just need to implement an extra check of the user's email before we save the data. We could use the existing repository method definition, but we should update the doc-string to include the new logic step.

If we have a guarantee that the email is unique, we can also add a convenience method to look up a user via the email address. The repository only provides the catch-all `find_users_by_attributes` method which returns a list that we would need to unpack every time. We can implement this once in the service layer.

With the repository interface as base class the `UserServiceInterface` is still quite compact:

```python
# app/domain/users/interfaces.py

class UserServiceInterface(UserRepositoryInterface):
    """definition of the UserService interface"""

    @abc.abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """find and return one user via the user's email"""
        raise NotImplementedError

    @abc.abstractmethod
    async def save_new_user(self, data: NewUserDTO) -> User:
        """check email for uniqueness, create new record and return user"""
        raise NotImplementedError
```

### UserService Implementation

The _UserService_ requires a _UserRepository_. We will provide one via dependency injection to the constructor. To help with typing we declare the type with the _UserRepositoryInterface_ class.

Most methods of the service are just thin wrappers for the repository methods of the same name. So the basic implementation looks like this:

```python
from typing import List, Optional

from .entities import NewUserDTO, User
from .interfaces import UserRepositoryInterface, UserServiceInterface

class UserService(UserServiceInterface):
    """provides access to the user repository for the use cases"""

    def __init__(self, repository: UserRepositoryInterface):
        self._repository = repository

    async def find_all(self) -> List[User]:
        """return a list of all users"""
        return await self._repository.find_all()

    # repeat for most other methods
```

The `get_user_by_email` just calls `find_users_by_attributes` with the email and unwraps the result or returns `None` if there are no results.

```python
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """find and return one user via the user's email"""
        users = await self._repository.find_users_by_attributes({"email": email})
        return None if len(users) == 0 else users[0]
```

In the `save_new_user` method we add new logic to check if a user with the same email address already exists. If it does we raise an error and let calling code handle it. If there is no such user we can just call `save_new_user` on the repository and return new user.

```python
    async def save_new_user(self, data: NewUserDTO) -> User:
        """check email for uniqueness, create new record and return user"""
        existing = await self.get_user_by_email(data.email)
        if existing is not None:
            raise ValueError("User with email '{data.email}' already exists.")

        return await self._repository.save_new_user(data)
```

### Testing the UserService

Because the service is mostly just a wrapper around the repository we can test it by confirming that the right repository functions are called.

To create an instance of the service we have to provide a repository. We will mock any methods that we are interested in on a case by case basis so we can set up a `MockUserRepository` where all methods are just stubs to satisfy the interface:

```python
# tests/unit/domain/users/test_user_service.py

class MockUserRepository(UserRepositoryInterface):
    async def find_all(self) -> List[User]:
        raise NotImplementedError
    async def find_users_by_attributes(self, attributes: dict) -> List[User]:
        raise NotImplementedError
    # ... other method stubs
```

The first set of tests will check that the correct repository method is called when we call a method of the service.

In each test we set up an instance of the mock repository and then define a mock handler for the repository method we want to spy on. We have to use Python's `AsyncMock` for this because all our methods are `async`.

With the mock we can create our service instance and call its method. Afterwards we use the methods of the mock repo handler to confirm that it has been called with the right arguments.

Here is an example for the `find_all` method:

```python
from unittest.mock import AsyncMock
# ... other imports

class TestMemoryUserRepository:
    """domain.users.service"""

    @pytest.mark.asyncio
    async def test_user_service_find_all(self):
        """[DOM-SRV-US-01] service.find_all calls repository.find_all"""
        repo = MockUserRepository()
        repo.find_all = AsyncMock()

        service = UserService(repo)
        await service.find_all()

        repo.find_all.assert_awaited()

```

When we test the `save_new_user` method we have to mock both repository methods that are called and also set an appropriate return value for `find_users_by_attributes` (an empty list for the success case). Our test then asserts that we called the repo first to check for an existing email and then to create and save the new user.

```python
    @pytest.mark.asyncio
    async def test_user_service_save_new_user(self):
        """[DOM-SRV-US-11] service.save_new_user checks the email before saving"""
        repo = MockUserRepository()
        repo.find_users_by_attributes = AsyncMock(return_value=[])
        repo.save_new_user = AsyncMock()

        service = UserService(repo)
        new_user = NewUserDTO.parse_obj(new_user_data)
        await service.save_new_user(new_user)

        repo.find_users_by_attributes.assert_awaited_with({"email": new_user.email})
        repo.save_new_user.assert_awaited_with(new_user)
```

Following this template we can add tests for the remaining service methods and return values.
