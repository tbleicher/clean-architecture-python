from typing import Any, List, Optional
from uuid import uuid4

from app.domain.users.entities import NewUserDTO, User
from app.domain.users.interfaces import UserRepositoryInterface

from ..utils import filter_entities_by_attributes, load_fixtures


class MemoryUserRepository(UserRepositoryInterface):
    """in-memory implementation of UserRepository"""

    def __init__(self, config: dict[str, Any]):
        """set up dict as 'storage' and load fixtures based on config"""
        self._users: dict[str, dict] = {}

        environment = config["environment"]
        fixtures = config["repositories"]["fixtures"]

        # load test data from fixture file when running tests
        if environment == "test" and "users" in fixtures:
            data = load_fixtures(fixtures["users"])
            self._users = {user["id"]: user for user in data}

    async def find_all(self) -> List[User]:
        """return a list of all users"""
        return [User(**user) for user in self._users.values()]

    async def find_users_by_attributes(self, attributes: dict) -> List[User]:
        """return list of users with given attribute values"""
        users = filter_entities_by_attributes(self._users, attributes)
        return [User(**user) for user in users]

    async def get_user_by_id(self, id: str) -> Optional[User]:
        return User(**self._users[id]) if id in self._users else None

    async def get_users_by_ids(self, ids: List[str]) -> List[User]:
        """find list of users via their ids"""
        users = [self._users[id] for id in ids if id in self._users]
        return [User(**user) for user in users]

    async def delete_user(self, id: str) -> bool:
        """delete a user from storage"""
        if id not in self._users:
            raise ValueError(f"User with id {id} does not exist.")

        del self._users[id]

        return True

    async def save_new_user(self, data: NewUserDTO) -> User:
        """create new record and return user"""
        id = str(uuid4())
        while id in self._users:
            id = str(uuid4())

        user = {**data.dict(), "id": id}
        self._users[id] = user

        return User(**user)

    async def update_user(self, user: User) -> User:
        """update an existing user in storage"""
        if user.id not in self._users:
            raise ValueError(f"User with id {user.id} does not exist.")

        self._users[user.id] = {**self._users[user.id], **user.dict()}

        return user
