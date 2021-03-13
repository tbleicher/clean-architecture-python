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
