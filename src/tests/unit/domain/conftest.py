import pytest
from typing import List, Optional

from app.domain.users.entities import NewUserDTO, User
from app.domain.users.interfaces import UserServiceInterface


class MockUserService(UserServiceInterface):
    async def find_all(self) -> List[User]:
        raise NotImplementedError

    async def find_users_by_attributes(self, attributes: dict) -> List[User]:
        raise NotImplementedError

    async def get_user_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError

    async def get_user_by_id(self, id: str) -> Optional[User]:
        raise NotImplementedError

    async def get_users_by_ids(self, ids: List[str]) -> List[User]:
        raise NotImplementedError

    async def delete_user(self, id: str) -> bool:
        raise NotImplementedError

    async def save_new_user(self, data: NewUserDTO) -> User:
        raise NotImplementedError

    async def update_user(self, user: User) -> User:
        raise NotImplementedError


@pytest.fixture()
def mock_user_service():
    yield MockUserService()
