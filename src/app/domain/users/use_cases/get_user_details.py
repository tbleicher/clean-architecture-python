from typing import Optional
from dependency_injector.wiring import inject, Provide

from app.di_containers import AppDependencies

from ..entities import SessionUser, User
from ..interfaces import UserServiceInterface


class GetUserDetailsUseCase:
    """return details of a single user"""

    @inject
    def __init__(
        self,
        user_service: UserServiceInterface = Provide[AppDependencies.services.user_service],  # type: ignore
    ):
        self.user_service = user_service

    async def execute(
        self, user_id: str, current_user: SessionUser = None
    ) -> Optional[User]:
        if not current_user:
            return None

        user = await self.user_service.get_user_by_id(user_id)

        if current_user.is_admin:
            return user

        if user and user.organization_id == current_user.organization_id:
            return user

        return None
