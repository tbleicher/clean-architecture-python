from typing import List

from ..entities import User
from ..interfaces import UserServiceInterface


class ListUsersUseCase:
    """return list of users"""

    def __init__(
        self,
        user_service: UserServiceInterface,
    ):
        self.user_service = user_service

    async def execute(self) -> List[User]:
        return await self.user_service.find_all()
