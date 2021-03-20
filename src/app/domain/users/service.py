from typing import List, Optional

from .entities import AuthUser, NewUserDTO, User
from .interfaces import UserRepositoryInterface, UserServiceInterface


class UserService(UserServiceInterface):
    """provides access to the user repository for the use cases"""

    def __init__(self, repository: UserRepositoryInterface):
        self._repository = repository

    async def find_all(self) -> List[User]:
        """return a list of all users"""
        return await self._repository.find_all()

    async def find_users_by_attributes(self, attributes: dict) -> List[User]:
        """return list of users with given attribute values"""
        return await self._repository.find_users_by_attributes(attributes)

    async def get_auth_user_by_email(self, email: str) -> Optional[AuthUser]:
        """find and return AuthUser via the user's email"""
        return await self._repository.get_auth_user_by_email(email)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """find and return one user via the user's email"""
        users = await self._repository.find_users_by_attributes({"email": email})
        return None if len(users) == 0 else users[0]

    async def get_user_by_id(self, id: str) -> Optional[User]:
        """find and return one user via the user's id"""
        return await self._repository.get_user_by_id(id)

    async def get_users_by_ids(self, ids: List[str]) -> List[User]:
        """find list of users via their ids"""
        return await self._repository.get_users_by_ids(ids)

    async def delete_user(self, id: str) -> bool:
        """delete a user from storage"""
        return await self._repository.delete_user(id)

    async def save_new_user(self, data: NewUserDTO) -> User:
        """check email for uniqueness, create new record and return user"""
        existing = await self.get_user_by_email(data.email)
        if existing is not None:
            raise ValueError("User with email '{data.email}' already exists.")

        return await self._repository.save_new_user(data)

    async def update_user(self, user: User) -> User:
        """update an existing user in storage"""
        return await self._repository.update_user(user)
