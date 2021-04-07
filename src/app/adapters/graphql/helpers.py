from typing import Any, Optional
from app.domain.users.entities import SessionUser


def get_current_user(info: Any) -> Optional[SessionUser]:
    current_user = info.context["request"]["state"]["user"]
    return current_user
