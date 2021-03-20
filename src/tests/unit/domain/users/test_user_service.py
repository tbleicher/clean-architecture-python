import pytest
from unittest.mock import AsyncMock

from app.domain.users.entities import NewUserDTO, User
from app.domain.users.service import UserService


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


class TestMemoryUserRepository:
    """domain.users.service"""

    @pytest.mark.asyncio
    async def test_user_service_find_all(self, mock_user_repository):
        """[DOM-SRV-US-01] service.find_all calls repository.find_all"""
        mock_user_repository.find_all = AsyncMock()

        service = UserService(mock_user_repository)
        await service.find_all()

        mock_user_repository.find_all.assert_awaited()

    @pytest.mark.asyncio
    async def test_user_service_find_users_by_attributes(self, mock_user_repository):
        """[DOM-SRV-US-02] service.find_users_by_attributes calls repository.find_users_by_attributes"""
        mock_user_repository.find_users_by_attributes = AsyncMock()

        service = UserService(mock_user_repository)
        await service.find_users_by_attributes({"key": "value"})

        mock_user_repository.find_users_by_attributes.assert_awaited_with(
            {"key": "value"}
        )

    @pytest.mark.asyncio
    async def test_user_service_get_user_by_id(self, mock_user_repository):
        """[DOM-SRV-US-03] service.get_user_by_id calls repository.get_user_by_id"""
        mock_user_repository.get_user_by_id = AsyncMock()

        service = UserService(mock_user_repository)
        await service.get_user_by_id("user-id")

        mock_user_repository.get_user_by_id.assert_awaited_with("user-id")

    @pytest.mark.asyncio
    async def test_user_service_get_users_by_ids(self, mock_user_repository):
        """[DOM-SRV-US-04] service.get_users_by_ids calls repository.get_users_by_ids"""
        mock_user_repository.get_users_by_ids = AsyncMock()

        service = UserService(mock_user_repository)
        await service.get_users_by_ids(["user-1", "user-2"])

        mock_user_repository.get_users_by_ids.assert_awaited_with(["user-1", "user-2"])

    @pytest.mark.asyncio
    async def test_user_service_delete_user(self, mock_user_repository):
        """[DOM-SRV-US-05] service.delete_user calls repository.delete_user"""
        mock_user_repository.delete_user = AsyncMock()

        service = UserService(mock_user_repository)
        await service.delete_user("user-id")

        mock_user_repository.delete_user.assert_awaited_with("user-id")

    @pytest.mark.asyncio
    async def test_user_service_update_user(self, mock_user_repository):
        """[DOM-SRV-US-06] service.update_user calls repository.update_user"""
        mock_user_repository.update_user = AsyncMock()

        service = UserService(mock_user_repository)
        user = User.parse_obj(user_data)
        await service.update_user(user)

        mock_user_repository.update_user.assert_awaited_with(user)

    @pytest.mark.asyncio
    async def test_user_service_get_auth_user_by_email(self, mock_user_repository):
        """[DOM-SRV-US-07] service.get_auth_user_by_email calls repository.get_auth_user_by_email"""
        mock_user_repository.get_auth_user_by_email = AsyncMock()

        service = UserService(mock_user_repository)
        await service.get_auth_user_by_email("email@example.com")

        mock_user_repository.get_auth_user_by_email.assert_awaited_with(
            "email@example.com"
        )

    @pytest.mark.asyncio
    async def test_user_service_save_new_user(self, mock_user_repository):
        """[DOM-SRV-US-11] service.save_new_user checks the email before saving"""
        mock_user_repository.find_users_by_attributes = AsyncMock(return_value=[])
        mock_user_repository.save_new_user = AsyncMock()

        service = UserService(mock_user_repository)
        new_user = NewUserDTO.parse_obj(new_user_data)
        await service.save_new_user(new_user)

        mock_user_repository.find_users_by_attributes.assert_awaited_with(
            {"email": new_user.email}
        )
        mock_user_repository.save_new_user.assert_awaited_with(new_user)

    @pytest.mark.asyncio
    async def test_user_service_save_new_user_raises_value_error(
        self, mock_user_repository
    ):
        """[DOM-SRV-US-12] service.save_new_user raises value error if an email exists"""
        mock_user_repository.find_users_by_attributes = AsyncMock(return_value=[{}])
        mock_user_repository.save_new_user = AsyncMock()

        service = UserService(mock_user_repository)
        new_user = NewUserDTO.parse_obj(new_user_data)

        with pytest.raises(ValueError):
            await service.save_new_user(new_user)

    @pytest.mark.asyncio
    async def test_user_service_get_user_by_email_queries_repo_with_email(
        self, mock_user_repository
    ):
        """[DOM-SRV-US-21] service.get_user_by_email call repo.find_users_by_attributes with email"""
        user = User.parse_obj(user_data)
        mock_user_repository.find_users_by_attributes = AsyncMock(return_value=[user])

        service = UserService(mock_user_repository)
        await service.get_user_by_email(user.email)

        mock_user_repository.find_users_by_attributes.assert_awaited_once_with(
            {"email": user.email}
        )

    @pytest.mark.asyncio
    async def test_user_service_get_user_by_email_returns_single_user_if_found(
        self, mock_user_repository
    ):
        """[DOM-SRV-US-22] service.get_user_by_email returns single user if one is found"""
        user = User.parse_obj(user_data)
        mock_user_repository.find_users_by_attributes = AsyncMock(return_value=[user])

        service = UserService(mock_user_repository)
        user1 = await service.get_user_by_email(user.email)

        assert user == user1

    @pytest.mark.asyncio
    async def test_user_service_get_user_by_email_returns_none_if_not_found(
        self, mock_user_repository
    ):
        """[DOM-SRV-US-23] service.get_user_by_email returns None if user was not found"""
        mock_user_repository.find_users_by_attributes = AsyncMock(return_value=[])

        service = UserService(mock_user_repository)
        user = await service.get_user_by_email("name@example.com")

        assert user is None
