from pydantic import BaseModel


class AuthUser(BaseModel):
    """limited user data object with password hash"""

    id: str
    email: str
    password_hash: str
    organization_id: str
    is_admin: bool

    class Config:
        allow_mutation = False


class NewUserDTO(BaseModel):
    """data to create a new user"""

    email: str
    first_name: str
    last_name: str
    organization_id: str
    password_hash: str
    is_admin: bool

    class Config:
        allow_mutation = False


class SessionUser(BaseModel):
    """user data extracted from access token"""

    id: str
    email: str
    organization_id: str
    is_admin: bool

    class Config:
        allow_mutation = False


class User(BaseModel):
    """representation of a user in our system"""

    id: str
    email: str
    first_name: str
    last_name: str
    organization_id: str
    is_admin: bool

    class Config:
        allow_mutation = False
