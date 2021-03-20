from app.domain.auth.entities import LoginInputDTO, TokenDataDTO
from app.domain.auth.use_cases import LoginUseCase

from ..types import LoginInput


async def login(input: LoginInput) -> TokenDataDTO:
    login = LoginUseCase()
    login_input = LoginInputDTO(email=input.email, password=input.password)

    return await login.execute(login_input)
