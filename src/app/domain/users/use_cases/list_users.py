from typing import List
from dependency_injector.wiring import inject, Provide

from app.di_containers import AppDependencies

from ..entities import User
from ..interfaces import UserServiceInterface


class ListUsersUseCase:
    """return list of users"""

    @inject
    def __init__(
        self,
        user_service: UserServiceInterface = Provide[AppDependencies.services.user_service],  # type: ignore
    ):
        self.user_service = user_service

    async def execute(self) -> List[User]:
        return await self.user_service.find_all()
