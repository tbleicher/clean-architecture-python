from typing import Optional
from dependency_injector.wiring import inject, Provide

from app.di_containers import AppDependencies
from app.domain.users.entities import SessionUser

from ..interfaces import AuthServiceInterface


class GetSessionUserUseCase:
    """identify and return user from request token"""

    @inject
    def __init__(
        self,
        auth_service: AuthServiceInterface = Provide[AppDependencies.services.auth_service],  # type: ignore
    ):
        self.auth_service: AuthServiceInterface = auth_service

    def execute(self, token: str) -> Optional[SessionUser]:
        """return list of groups in the same organization"""
        return self.auth_service.get_session_user(token)
