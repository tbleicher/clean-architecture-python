from fastapi import Request

from app.domain.auth.use_cases import GetSessionUserUseCase


def get_token_from_header(request: Request) -> str:
    """return auth token from request headers"""
    try:
        auth_header = request.headers["authorization"]
    except KeyError:
        return ""

    if auth_header.lower().startswith("bearer "):
        return auth_header.split(" ")[1]

    return auth_header


async def get_token_user(request: Request) -> Request:
    """add session user from auth token to request"""
    try:
        token = get_token_from_header(request)
        use_case = GetSessionUserUseCase()
        request.state.user = await use_case.execute(token)
    except KeyError:
        request.state.user = None

    return request
