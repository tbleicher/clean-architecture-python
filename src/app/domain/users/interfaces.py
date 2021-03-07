import abc
from typing import List, Optional

from app.domain.utils import implements_interface

from .entities import NewUserDTO, User


class UserRepositoryInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return implements_interface(cls, subclass) or NotImplemented

    @abc.abstractmethod
    async def find_all(self) -> List[User]:
        """return a list of all users"""
        raise NotImplementedError

    @abc.abstractmethod
    async def find_users_by_attributes(self, attributes: dict) -> List[User]:
        """return list of users with given attribute values"""
        raise NotImplementedError

    @abc.abstractmethod
    async def get_user_by_id(self, id: str) -> Optional[User]:
        """find and return one user via the user's id"""
        raise NotImplementedError

    @abc.abstractmethod
    async def get_users_by_ids(self, ids: List[str]) -> List[User]:
        """find list of users via their ids"""
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_user(self, id: str) -> bool:
        """delete a user from storage"""
        raise NotImplementedError

    @abc.abstractmethod
    async def save_new_user(self, data: NewUserDTO) -> User:
        """create new record and return user"""
        raise NotImplementedError

    @abc.abstractmethod
    async def update_user(self, user: User) -> User:
        """update an existing user in storage"""
        raise NotImplementedError
