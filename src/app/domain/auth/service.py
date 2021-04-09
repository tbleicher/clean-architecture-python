from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from typing import Any, Optional

from app.domain.users.entities import AuthUser, SessionUser
from app.domain.users.interfaces import UserRepositoryInterface

from .errors import AuthError
from .entities import LoginInputDTO, TokenDataDTO
from .interfaces import AuthServiceInterface

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(payload: dict, config: Any) -> str:
    """generate signed token with 'payload' as claims"""
    to_encode = payload.copy()
    expire = datetime.utcnow() + timedelta(seconds=config["token_ttl"])
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, config["secret"], algorithm=config["algorithm"])
    return token


def verify_password(plain_password, hashed_password) -> bool:
    """compare password with stored password hash"""
    return bcrypt_context.verify(plain_password, hashed_password)


class AuthService(AuthServiceInterface):
    def __init__(self, repository: UserRepositoryInterface, config: Any):
        self.repository = repository
        self.config = config

    async def authenticate_user(self, input: LoginInputDTO) -> TokenDataDTO:
        """validate user's login data and return session token data"""
        user = await self.repository.get_auth_user_by_email(input.email)
        if not user:
            raise AuthError()

        verified = verify_password(input.password, user.password_hash)
        if not verified:
            raise AuthError()

        token = self.get_token(user)
        return TokenDataDTO(token=token)

    def get_token(self, user) -> str:
        """create token with session user data as payload"""
        session_user = SessionUser.parse_obj(user.dict())
        payload = {"sub": user.id, "user": session_user.dict()}

        return create_access_token(payload, self.config)

    def get_session_user_from_token(self, token: str) -> Optional[SessionUser]:
        """extract user data from session token"""
        algorithm = self.config["algorithm"]
        secret = self.config["secret"]

        try:
            decoded = jwt.decode(token, secret, algorithms=[algorithm])
            session_user = SessionUser(**decoded["user"])
            return session_user
        except Exception:
            return None
