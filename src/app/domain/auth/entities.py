from pydantic import BaseModel


class LoginInputDTO(BaseModel):
    email: str
    password: str

    class Config:
        allow_mutation = False


class TokenDataDTO(BaseModel):
    token: str

    class Config:
        allow_mutation = False
