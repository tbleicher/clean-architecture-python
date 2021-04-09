from typing import List
from dependency_injector.wiring import inject, Provide

from app.di_containers import AppDependencies

from ..entities import SessionUser, User
from ..interfaces import UserServiceInterface


class ListUsersUseCase:
    """return list of users"""

    @inject
    def __init__(
        self,
        user_service: UserServiceInterface = Provide[AppDependencies.services.user_service],  # type: ignore
    ):
        self.user_service = user_service

    async def execute(self, current_user: SessionUser = None) -> List[User]:
        if not current_user:
            return []

        if current_user.is_admin:
            return await self.user_service.find_all()

        attributes = {"organization_id": current_user.organization_id}
        return await self.user_service.find_users_by_attributes(attributes)
