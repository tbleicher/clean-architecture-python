import abc
from typing import Optional

from app.domain.users.entities import SessionUser, User
from .entities import LoginInputDTO, TokenDataDTO


class AuthServiceInterface(metaclass=abc.ABCMeta):
    """test comment"""

    @abc.abstractmethod
    async def authenticate_user(self, input: LoginInputDTO) -> TokenDataDTO:
        """authenticate user via email and password and return auth token"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_token(self, user: User):
        """return token data for user"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_session_user(self, request) -> Optional[SessionUser]:
        """return SessionUser from request"""
        raise NotImplementedError
