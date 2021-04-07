from typing import List, Optional

from app.domain.users.entities import User, UserProfile
from app.domain.users.use_cases import (
    GetUserProfileUseCase,
    ListUsersUseCase,
)

from app.adapters.graphql.helpers import get_current_user


async def get_user_profile(info) -> Optional[UserProfile]:
    """get use profile from current user in session info"""
    current_user = get_current_user(info)
    use_case = GetUserProfileUseCase()
    return await use_case.execute(current_user)


async def list_users() -> List[User]:
    """call use case and convert user entities to GraphQL Users"""
    use_case = ListUsersUseCase()
    return await use_case.execute()
