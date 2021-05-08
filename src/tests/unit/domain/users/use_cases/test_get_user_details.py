import pytest
from unittest.mock import AsyncMock

from app.domain.users.entities import SessionUser, User
from app.domain.users.use_cases import GetUserDetailsUseCase

USER = User(
    id="USER-CLOE",
    email="cloe@example.com",
    first_name="Cloe",
    is_admin=False,
    last_name="CEO",
    organization_id="GROUP-SHOESTRING-LTD",
)
ORGANISATION_USER = SessionUser(
    id="user-id",
    email="user@example.com",
    organization_id=USER.organization_id,
    is_admin=False,
)
OTHER_USER = SessionUser(
    id="user-id",
    email="user@example.com",
    organization_id="other-org-id",
    is_admin=False,
)
ADMIN_USER = SessionUser(
    id="user-id",
    email="user@example.com",
    organization_id="",
    is_admin=True,
)


class TestGetUserDetailsUseCase:
    """domain.users.use_cases.get_user_details"""

    async def _call_use_case(self, mock_user_service, current_user, return_value=None):
        mock_user_service.get_user_by_id = AsyncMock(return_value=return_value)

        use_case = GetUserDetailsUseCase(user_service=mock_user_service)
        user = await use_case.execute(USER.id, current_user)

        mock_user_service.get_user_by_id.assert_awaited_with(USER.id)

        return user

    @pytest.mark.asyncio
    async def test_use_case_get_user_details_with_user_without_current_user(
        self, mock_user_service
    ):
        """[DOM-UC-US-DET-01] with valid id returns None without current user"""
        mock_user_service.get_user_by_id = AsyncMock(return_value=USER)

        use_case = GetUserDetailsUseCase(user_service=mock_user_service)
        user = await use_case.execute(USER.id, current_user=None)

        assert user == None

    @pytest.mark.asyncio
    async def test_use_case_get_user_details_with_user_as_organisation_user(
        self, mock_user_service
    ):
        """[DOM-UC-US-DET-02] with valid id returns user when called by user from same organisation"""

        result = await self._call_use_case(mock_user_service, ORGANISATION_USER, USER)
        assert result == USER

    @pytest.mark.asyncio
    async def test_use_case_get_user_details_with_user_as_other_user(
        self, mock_user_service
    ):
        """[DOM-UC-US-DET-03] with valid id returns None when called by user from other organisation"""

        result = await self._call_use_case(mock_user_service, OTHER_USER, USER)
        assert result == None

    @pytest.mark.asyncio
    async def test_use_case_get_user_details_with_user_as_admin_user(
        self, mock_user_service
    ):
        """[DOM-UC-US-DET-04] with valid id returns user when called by an admin"""

        result = await self._call_use_case(mock_user_service, ADMIN_USER, USER)
        assert result == USER

    @pytest.mark.asyncio
    async def test_use_case_get_user_details_without_user_without_current_user(
        self, mock_user_service
    ):
        """[DOM-UC-US-DET-05] without valid id returns None without current user"""
        mock_user_service.get_user_by_id = AsyncMock(return_value=USER)

        use_case = GetUserDetailsUseCase(user_service=mock_user_service)
        user = await use_case.execute(USER.id, current_user=None)

        assert user == None

    @pytest.mark.asyncio
    async def test_use_case_get_user_details_without_user_as_organisation_user(
        self, mock_user_service
    ):
        """[DOM-UC-US-DET-06] without valid id returns None when called by user from same organisation"""

        result = await self._call_use_case(mock_user_service, ORGANISATION_USER)
        assert result == None

    @pytest.mark.asyncio
    async def test_use_case_get_user_details_without_user_as_other_user(
        self, mock_user_service
    ):
        """[DOM-UC-US-DET-07] without valid id returns None when called by user from other organisation"""

        result = await self._call_use_case(mock_user_service, OTHER_USER)
        assert result == None

    @pytest.mark.asyncio
    async def test_use_case_get_user_details_without_user_as_admin_user(
        self, mock_user_service
    ):
        """[DOM-UC-US-DET-08] without valid id returns None when called by an admin"""

        result = await self._call_use_case(mock_user_service, ADMIN_USER)
        assert result == None
