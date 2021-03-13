# 4. First Use Case

All business logic will be express in _Use Cases_. This includes access control because this is - after all - just another business requirement.

We will split our use case call into two steps: setup and execution. In the setup we create an instance of the use case and provide the necessary dependencies like services or configuration option. The execution then receives call specific arguments and does the heavy lifting.

## 4e. List Users Use Case

At this point our requirements for the _List Users_ use case are very basic: Return a list of all users. Without the means to identify the querying user we can't do much else.

Since we have a service method that provides the full list all we need to do is call it and return the result. We will add more logic later but for now the full use case implementation looks like this:

```python
# app/domain/users/use_cases/list_users.py

from typing import List

from ..entities import User
from ..interfaces import UserServiceInterface

class ListUsersUseCase:
    """return list of users"""

    def __init__(self, user_service: UserServiceInterface):
        self.user_service = user_service

    async def execute(self) -> List[User]:
        return await self.user_service.find_all()
```

### Testing

We need to provide a dependency (the user service) to create an instance of the _ListUsersUseCase_ class. Like with the mock repository for the _UserService_ we can set up a _MockUserService_ class. This time we will also define a Pytest fixture because we will need the MockUserService for several use cases. We can set up a new `conftest.py` file at the level of the domain tests to make this fixture available to all tests that deal with domain logic:

```python
# tests/unit/domain/conftest.py

import pytest
from typing import List, Optional

from app.domain.users.entities import NewUserDTO, User
from app.domain.users.interfaces import UserServiceInterface

class MockUserService(UserServiceInterface):
    async def find_all(self) -> List[User]:
        raise NotImplementedError

    # ... more mock stub methods

@pytest.fixture()
def mock_user_service():
    yield MockUserService()
```

Using the mock service and AsyncMock to define a spy for the method we want to test we can define a simple test to verify that the service's `find_all` method is called by the use case instance:

```python
import pytest
from unittest.mock import AsyncMock

from app.domain.users.use_cases import ListUsersUseCase

class TestListUsersUseCase:
    """domain.users.use_cases.list_users"""

    @pytest.mark.asyncio
    async def test_use_case_list_users(self, mock_user_service):
        """[DOM-UC-LSTUS-00] ListUsersUseCase calls user_service.find_all"""

        mock_user_service.find_all = AsyncMock()

        use_case = ListUsersUseCase(user_service=mock_user_service)
        await use_case.execute()

        mock_user_service.find_all.assert_awaited()
```

Note that I haven't assigned a permanent ID to this test yet. This is not the final implementation of the use case so the return value is not correct. We will come back and complete the use case after we have an authentication system implemented and can identify the user who's making the request.
