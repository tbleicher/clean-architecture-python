from pydantic import BaseModel


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
