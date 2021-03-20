from dependency_injector.wiring import inject, Provide

from app.di_containers import AppDependencies

from ..entities import LoginInputDTO, TokenDataDTO
from ..interfaces import AuthServiceInterface


class LoginUseCase:
    """process user login"""

    @inject
    def __init__(
        self,
        auth_service: AuthServiceInterface = Provide[AppDependencies.services.auth_service],  # type: ignore
    ):
        self.auth_service: AuthServiceInterface = auth_service

    async def execute(self, login_input: LoginInputDTO) -> TokenDataDTO:
        """verify login credentials and return token data"""
        return await self.auth_service.authenticate_user(login_input)
