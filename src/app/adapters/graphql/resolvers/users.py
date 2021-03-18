from typing import List

from app.domain.users.entities import User
from app.domain.users.use_cases import (
    ListUsersUseCase,
)

async def list_users() -> List[User]:
    """call use case and convert user entities to GraphQL Users"""
    use_case = ListUsersUseCase()
    return await use_case.execute()
