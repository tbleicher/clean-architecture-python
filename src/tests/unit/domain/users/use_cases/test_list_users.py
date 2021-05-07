import pytest
from unittest.mock import AsyncMock

from app.domain.users.entities import SessionUser
from app.domain.users.use_cases import ListUsersUseCase


class TestListUsersUseCase:
    """domain.users.use_cases.list_users"""

    @pytest.mark.asyncio
    async def test_use_case_list_users_without_current_user(self, mock_user_service):
        """[DOM-UC-US-LST-01] ListUsersUseCase return empty list without current user"""
        use_case = ListUsersUseCase(user_service=mock_user_service)
        result = await use_case.execute()

        assert result == []

    @pytest.mark.asyncio
    async def test_use_case_list_users_with_regular_user(self, mock_user_service):
        """[DOM-UC-US-LST-02] ListUsersUseCase searches users by organisation_id when called by a regular user"""

        mock_user_service.find_users_by_attributes = AsyncMock()
        session_user = SessionUser(
            id="user-id",
            email="user@example.com",
            organization_id="example-org-id",
            is_admin=False,
        )
        expected = {"organization_id": session_user.organization_id}

        use_case = ListUsersUseCase(user_service=mock_user_service)
        await use_case.execute(session_user)

        mock_user_service.find_users_by_attributes.assert_awaited_with(expected)

    @pytest.mark.asyncio
    async def test_use_case_list_users_with_admin_user(self, mock_user_service):
        """[DOM-UC-US-LST-03] ListUsersUseCase returns all users when called by an admin"""

        mock_user_service.find_all = AsyncMock()
        session_user = SessionUser(
            id="user-id",
            email="user@example.com",
            organization_id="example-org-id",
            is_admin=True,
        )

        use_case = ListUsersUseCase(user_service=mock_user_service)
        await use_case.execute(session_user)

        mock_user_service.find_all.assert_awaited()
