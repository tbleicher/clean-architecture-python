import pytest
from unittest.mock import AsyncMock
from jose import jwt

from app.domain.users.entities import AuthUser, User
from app.domain.auth.entities import LoginInputDTO
from app.domain.auth.errors import AuthError
from app.domain.auth.service import AuthService


user_data = {
    "id": "user-id",
    "first_name": "First",
    "last_name": "Last",
    "email": "firstlast@example.com",
    "organization_id": "Example Ltd.",
    "password_hash": "$2b$12$/bxSAKp5FLBWOs/zq4n8xOmoR2hlXaEQ/60I58xTfKpbYSQOF7N0i",  # "password"
    "is_admin": False,
}

auth_user = AuthUser.parse_obj(user_data)

user = User.parse_obj(user_data)

config = {
    "algorithm": "HS256",
    "secret": "secret",
    "token_ttl": 3600,
}


class TestAuthService:
    """domain.auth.service"""

    @pytest.mark.asyncio
    async def test_auth_service_authenticate_user(self, mock_user_repository):
        """[DOM-SRV-AU-01] service.authenticate_user returns a token"""
        mock_user_repository.get_auth_user_by_email = AsyncMock(return_value=auth_user)
        service = AuthService(config=config, repository=mock_user_repository)

        input = LoginInputDTO.parse_obj({"email": user.email, "password": "password"})
        token_data = await service.authenticate_user(input)

        assert token_data
        assert token_data.token[0:2] == "ey"

    @pytest.mark.asyncio
    async def test_auth_service_authenticate_user_without_user(
        self, mock_user_repository
    ):
        """[DOM-SRV-AU-02] service.authenticate_user raises AuthError when no user is found"""
        mock_user_repository.get_auth_user_by_email = AsyncMock(return_value=None)
        service = AuthService(config=config, repository=mock_user_repository)
        input = LoginInputDTO.parse_obj({"email": user.email, "password": "password"})

        with pytest.raises(AuthError):
            await service.authenticate_user(input)

    @pytest.mark.asyncio
    async def test_auth_service_authenticate_user_with_wrong_password(
        self, mock_user_repository
    ):
        """[DOM-SRV-AU-03] service.authenticate_user raises AuthError with wrong password"""
        mock_user_repository.get_auth_user_by_email = AsyncMock(return_value=None)
        service = AuthService(config=config, repository=mock_user_repository)
        input = LoginInputDTO.parse_obj(
            {"email": user.email, "password": "wrong password"}
        )

        with pytest.raises(AuthError):
            await service.authenticate_user(input)

    def test_auth_service_get_token(self, mock_user_repository):
        """[DOM-SRV-AU-11] service.get_token returns a token with user data"""
        service = AuthService(config=config, repository=mock_user_repository)
        token = service.get_token(user)

        decoded = jwt.decode(token, config["secret"], algorithms=[config["algorithm"]])
        assert decoded["sub"] == user.id

        token_user = decoded["user"]
        assert token_user["id"] == user.id
        assert token_user["email"] == user.email
        assert token_user["organization_id"] == user.organization_id
        assert token_user["is_admin"] == user.is_admin

    def test_auth_service_get_session_user_from_token(self, mock_user_repository):
        """[DOM-SRV-AU-21] service.get_token returns a SessionUser from the token"""
        service = AuthService(config=config, repository=mock_user_repository)
        token = service.get_token(user)
        session_user = service.get_session_user_from_token(token)

        assert session_user.id == user.id
        assert session_user.email == user.email

    def test_auth_service_get_session_user_from_token_with_error(
        self, mock_user_repository
    ):
        """[DOM-SRV-AU-22] service.get_token returns None when token is not valid"""
        service = AuthService(config=config, repository=mock_user_repository)
        token = service.get_token(user)
        session_user = service.get_session_user_from_token(token[0 : len(token) - 5])

        assert session_user is None
