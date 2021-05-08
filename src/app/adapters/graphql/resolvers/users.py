from typing import List, Optional

from app.domain.users.entities import User, UserProfile
from app.domain.users.use_cases import (
    GetUserDetailsUseCase,
    GetUserProfileUseCase,
    ListUsersUseCase,
)

from app.adapters.graphql.helpers import get_current_user


async def get_user_details(info, user_id) -> Optional[User]:
    """get user details for user identified by user_id"""
    current_user = get_current_user(info)
    use_case = GetUserDetailsUseCase()
    return await use_case.execute(user_id, current_user)


async def get_user_profile(info) -> Optional[UserProfile]:
    """get use profile from current user in session info"""
    current_user = get_current_user(info)
    use_case = GetUserProfileUseCase()
    return await use_case.execute(current_user)


async def list_users(info) -> List[User]:
    """call ListUsersUseCase.execute() with current_user as argument"""
    current_user = get_current_user(info)
    use_case = ListUsersUseCase()
    return await use_case.execute(current_user)
