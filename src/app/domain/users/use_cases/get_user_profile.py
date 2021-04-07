from typing import Optional
from ..entities import SessionUser, UserProfile


class GetUserProfileUseCase:
    """return the current user's profile data"""

    async def execute(
        self, current_user: Optional[SessionUser] = None
    ) -> Optional[UserProfile]:
        if not current_user:
            return None

        return UserProfile(**current_user.dict())
