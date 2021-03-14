from typing import List

from app.domain.users.entities import User
from app.domain.users.use_cases import (
    ListUsersUseCase,
)


# don't get attached - this is just temporary
from app.adapters.repositories.users.memory_user_repository import MemoryUserRepository
from app.domain.users.service import UserService

config_with_users = {
    "environment": "test",
    "repositories": {
        "fixtures": {
            "users": "tests/fixtures/users.json",
        }
    },
}


async def list_users() -> List[User]:
    """call use case and convert user entities to GraphQL Users"""
    tmp_user_repo = MemoryUserRepository(config=config_with_users)
    tmp_user_service = UserService(repository=tmp_user_repo)

    use_case = ListUsersUseCase(user_service=tmp_user_service)
    return await use_case.execute()
