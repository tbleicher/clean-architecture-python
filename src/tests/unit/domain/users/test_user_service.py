import pytest
from typing import List, Optional
from unittest.mock import AsyncMock

from app.domain.users.entities import NewUserDTO, User
from app.domain.users.service import UserService
from app.domain.users.interfaces import UserRepositoryInterface

new_user_data = {
    "first_name": "First",
    "last_name": "Last",
    "email": "firstlast@example.com",
    "organization_id": "Example Ltd.",
    "password_hash": "password_hash",
    "is_admin": False,
}

user_data = {
    "id": "user-id",
    "first_name": "First",
    "last_name": "Last",
    "email": "firstlast@example.com",
    "organization_id": "Example Ltd.",
    "is_admin": False,
}


class MockUserRepository(UserRepositoryInterface):
    async def find_all(self) -> List[User]:
        raise NotImplementedError

    async def find_users_by_attributes(self, attributes: dict) -> List[User]:
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

    @pytest.mark.asyncio
    async def test_user_service_find_users_by_attributes(self):
        """[DOM-SRV-US-02] service.find_users_by_attributes calls repository.find_users_by_attributes"""
        repo = MockUserRepository()
        repo.find_users_by_attributes = AsyncMock()

        service = UserService(repo)
        await service.find_users_by_attributes({"key": "value"})

        repo.find_users_by_attributes.assert_awaited_with({"key": "value"})

    @pytest.mark.asyncio
    async def test_user_service_get_user_by_id(self):
        """[DOM-SRV-US-03] service.get_user_by_id calls repository.get_user_by_id"""
        repo = MockUserRepository()
        repo.get_user_by_id = AsyncMock()

        service = UserService(repo)
        await service.get_user_by_id("user-id")

        repo.get_user_by_id.assert_awaited_with("user-id")

    @pytest.mark.asyncio
    async def test_user_service_get_users_by_ids(self):
        """[DOM-SRV-US-04] service.get_users_by_ids calls repository.get_users_by_ids"""
        repo = MockUserRepository()
        repo.get_users_by_ids = AsyncMock()

        service = UserService(repo)
        await service.get_users_by_ids(["user-1", "user-2"])

        repo.get_users_by_ids.assert_awaited_with(["user-1", "user-2"])

    @pytest.mark.asyncio
    async def test_user_service_delete_user(self):
        """[DOM-SRV-US-05] service.delete_user calls repository.delete_user"""
        repo = MockUserRepository()
        repo.delete_user = AsyncMock()

        service = UserService(repo)
        await service.delete_user("user-id")

        repo.delete_user.assert_awaited_with("user-id")

    @pytest.mark.asyncio
    async def test_user_service_update_user(self):
        """[DOM-SRV-US-06] service.update_user calls repository.update_user"""
        repo = MockUserRepository()
        repo.update_user = AsyncMock()

        service = UserService(repo)
        user = User.parse_obj(user_data)
        await service.update_user(user)

        repo.update_user.assert_awaited_with(user)

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

    @pytest.mark.asyncio
    async def test_user_service_save_new_user_raises_value_error(self):
        """[DOM-SRV-US-12] service.save_new_user raises value error if an email exists"""
        repo = MockUserRepository()
        repo.find_users_by_attributes = AsyncMock(return_value=[{}])
        repo.save_new_user = AsyncMock()

        service = UserService(repo)
        new_user = NewUserDTO.parse_obj(new_user_data)

        with pytest.raises(ValueError):
            await service.save_new_user(new_user)

    @pytest.mark.asyncio
    async def test_user_service_get_user_by_email_queries_repo_with_email(self):
        """[DOM-SRV-US-21] service.get_user_by_email call repo.find_users_by_attributes with email"""
        user = User.parse_obj(user_data)
        repo = MockUserRepository()
        repo.find_users_by_attributes = AsyncMock(return_value=[user])

        service = UserService(repo)
        await service.get_user_by_email(user.email)

        repo.find_users_by_attributes.assert_awaited_once_with({"email": user.email})

    @pytest.mark.asyncio
    async def test_user_service_get_user_by_email_returns_single_user_if_found(self):
        """[DOM-SRV-US-22] service.get_user_by_email returns single user if one is found"""
        user = User.parse_obj(user_data)
        repo = MockUserRepository()
        repo.find_users_by_attributes = AsyncMock(return_value=[user])

        service = UserService(repo)
        user1 = await service.get_user_by_email(user.email)

        assert user == user1

    @pytest.mark.asyncio
    async def test_user_service_get_user_by_email_returns_none_if_not_found(self):
        """[DOM-SRV-US-23] service.get_user_by_email returns None if user was not found"""
        repo = MockUserRepository()
        repo.find_users_by_attributes = AsyncMock(return_value=[])

        service = UserService(repo)
        user = await service.get_user_by_email("name@example.com")

        assert user is None
