import pytest

from app.adapters.repositories.users.memory_user_repository import MemoryUserRepository
from app.domain.users.entities import NewUserDTO, User
from app.di_containers import AppDependencies

new_user_data = {
    "first_name": "First",
    "last_name": "Last",
    "email": "firstlast@example.com",
    "organization_id": "Example Ltd.",
    "password_hash": "password_hash",
    "is_admin": False,
}

non_test_env = {
    "environment": "not_test",
    "repositories": {
        "fixtures": {
            "users": "tests/fixtures/users.json",
        }
    },
}

no_fixture_path = {
    "environment": "test",
    "repositories": {"fixtures": {}},
}


class TestMemoryUserRepository:
    """adapters.repositories.memory_user_repository"""

    def test_memory_user_repository_instance(self, dependencies, all_users):
        """[REPO-US-MEM-01] memory repository instance requires a configuration object"""
        repo = MemoryUserRepository(dependencies.config)

        assert len(repo._users) == len(all_users)

    def test_memory_user_repository_non_test_env(self):
        """[REPO-US-MEM-02] memory repository does only load fixtures in test environment"""
        dependencies = AppDependencies()
        dependencies.init_resources()
        dependencies.config.from_dict(non_test_env)

        repo = MemoryUserRepository(dependencies.config)

        assert len(repo._users) == 0

    def test_memory_user_repository_without_fixture_path(self):
        """[REPO-US-MEM-03] memory repository does not load fixtures without fixture path"""
        dependencies = AppDependencies()
        dependencies.init_resources()
        dependencies.config.from_dict(no_fixture_path)

        repo = MemoryUserRepository(dependencies.config)

        assert len(repo._users) == 0

    @pytest.mark.asyncio
    async def test_memory_user_repository_find_all_returns_list_of_users(
        self, dependencies
    ):
        """[REPO-US-MEM-11] repo.find_all returns a list of User entities"""
        repo = MemoryUserRepository(dependencies.config)
        repo_users = await repo.find_all()

        assert isinstance(repo_users, list)
        assert isinstance(repo_users[0], User)

    @pytest.mark.asyncio
    async def test_memory_user_repository_find_all_returns_all_users(
        self, dependencies, all_users
    ):
        """[REPO-US-MEM-12] repo.find_all returns all users"""
        repo = MemoryUserRepository(dependencies.config)
        repo_users = await repo.find_all()

        assert len(repo_users) == len(all_users)

    @pytest.mark.asyncio
    async def test_memory_user_repository_get_user_by_id_returns_users(
        self, dependencies, all_users
    ):
        """[REPO-US-MEM-21] repo.get_user_by_id returns a User"""
        repo = MemoryUserRepository(dependencies.config)
        user = await repo.get_user_by_id(all_users[0]["id"])

        assert user is not None
        assert isinstance(user, User)
        assert user.id == all_users[0]["id"]

    @pytest.mark.asyncio
    async def test_memory_user_repository_get_user_by_id_returns_none(
        self, dependencies
    ):
        """[REPO-US-MEM-22] repo.get_user_by_id returns all users"""
        repo = MemoryUserRepository(dependencies.config)
        user = await repo.get_user_by_id("no-such-id")

        assert user is None

    @pytest.mark.asyncio
    async def test_memory_user_repository_get_user_by_id_returns_a_list_of_users(
        self, dependencies, all_users
    ):
        """[REPO-US-MEM-31] repo.get_users_by_ids returns a list of users"""
        repo = MemoryUserRepository(dependencies.config)
        user_ids = [all_users[0]["id"], all_users[2]["id"], all_users[7]["id"]]
        users = await repo.get_users_by_ids(user_ids)

        assert isinstance(users, list)
        assert isinstance(users[0], User)

    @pytest.mark.asyncio
    async def test_memory_user_repository_get_users_by_ids_returns_exiting_users(
        self, dependencies, all_users
    ):
        """[REPO-US-MEM-32] repo.get_users_by_ids returns users for valid ids"""
        repo = MemoryUserRepository(dependencies.config)
        user_ids = [all_users[0]["id"], "no-such-id", all_users[7]["id"]]
        users = await repo.get_users_by_ids(user_ids)

        assert len(users) == 2
        assert users[0].id == all_users[0]["id"]
        assert users[1].id == all_users[7]["id"]

    @pytest.mark.asyncio
    async def test_memory_user_repository_get_users_by_ids_returns_empty_list(
        self, dependencies
    ):
        """[REPO-US-MEM-33] repo.get_users_by_ids returns empty list with no valid ids"""
        repo = MemoryUserRepository(dependencies.config)
        user_ids = ["apples-and-pears", "no-such-id", "does-not-exist"]
        users = await repo.get_users_by_ids(user_ids)

        assert isinstance(users, list)
        assert len(users) == 0

    @pytest.mark.asyncio
    async def test_memory_user_repository_find_users_by_attributes_returns_list_of_users(
        self, dependencies
    ):
        """[REPO-US-MEM-41] repo.find_users_by_attributes returns a list of users"""
        repo = MemoryUserRepository(dependencies.config)
        attributes = {
            "organization_id": "GROUP-SHOESTRING-LTD",
        }
        users = await repo.find_users_by_attributes(attributes)

        assert isinstance(users, list)
        assert isinstance(users[0], User)

    @pytest.mark.asyncio
    async def test_memory_user_repository_find_users_by_attributes_returns_selection_of_users(
        self, dependencies, all_users
    ):
        """[REPO-US-MEM-42] repo.find_users_by_attributes returns a selection of users"""
        repo = MemoryUserRepository(dependencies.config)
        attributes = {
            "organization_id": "GROUP-SHOESTRING-LTD",
        }
        expected = [
            user
            for user in all_users
            if user["organization_id"] == "GROUP-SHOESTRING-LTD"
        ]
        users = await repo.find_users_by_attributes(attributes)

        assert len(users) == len(expected)

    @pytest.mark.asyncio
    async def test_memory_user_repository_find_users_by_attributes_returns_an_empty_list(
        self, dependencies
    ):
        """[REPO-US-MEM-43] repo.find_users_by_attributes returns an empty list if no users are found"""
        repo = MemoryUserRepository(dependencies.config)
        attributes = {
            "organization_id": "NO-SUCH_ID",
        }
        users = await repo.find_users_by_attributes(attributes)

        assert isinstance(users, list)
        assert len(users) == 0

    @pytest.mark.asyncio
    async def test_memory_user_repository_save_new_user_returns_new_user(
        self, dependencies
    ):
        """[REPO-US-MEM-51] repo.save_new_user creates new user from NewUserDTO entity"""
        repo = MemoryUserRepository(dependencies.config)
        data = NewUserDTO(**new_user_data)
        user = await repo.save_new_user(data)

        assert isinstance(user, User)

    @pytest.mark.asyncio
    async def test_memory_user_repository_save_new_user_adds_data_to_storage(
        self, dependencies, all_users
    ):
        """[REPO-US-MEM-52] repo.save_new_user adds new user record to storage"""
        repo = MemoryUserRepository(dependencies.config)
        data = NewUserDTO(**new_user_data)
        await repo.save_new_user(data)

        assert len(repo._users) == len(all_users) + 1

    @pytest.mark.asyncio
    async def test_memory_user_repository_update_user_stores_new_user_data(
        self, dependencies, all_users
    ):
        """[REPO-US-MEM-61] repo.update_user saves new user data to storage"""
        repo = MemoryUserRepository(dependencies.config)
        user1 = await repo.get_user_by_id(all_users[1]["id"])
        user2 = User.parse_obj({**user1.dict(), "email": f"updated_{user1.email}"})
        user3 = await repo.update_user(user2)

        assert user1.id == user3.id
        assert user1.email != user3.email
        assert user3.email == f"updated_{user1.email}"

    @pytest.mark.asyncio
    async def test_memory_user_repository_update_user_raises_value_error(
        self, dependencies, all_users
    ):
        """[REPO-US-MEM-62] repo.update_user raises ValueError when user id is not found"""
        repo = MemoryUserRepository(dependencies.config)
        user1 = await repo.get_user_by_id(all_users[1]["id"])
        user2 = User.parse_obj(
            {**user1.dict(), "email": f"updated_{user1.email}", "id": "no-such-id"}
        )

        with pytest.raises(ValueError):
            await repo.update_user(user2)

    @pytest.mark.asyncio
    async def test_memory_user_repository_delete_user_removes_record_from_storage(
        self, dependencies, all_users
    ):
        """[REPO-US-MEM-71] repo.delete_user removes user with the given id"""
        repo = MemoryUserRepository(dependencies.config)

        user1 = await repo.get_user_by_id(all_users[1]["id"])
        assert isinstance(user1, User)

        result = await repo.delete_user(user1.id)
        assert result == True

        user2 = await repo.get_user_by_id(user1.id)
        assert user2 is None

        assert len(repo._users) == len(all_users) - 1

    @pytest.mark.asyncio
    async def test_memory_user_repository_delete_user_raises_value_error(
        self, dependencies
    ):
        """[REPO-US-MEM-72] repo.delete_user raises ValueError when user id is not found"""
        repo = MemoryUserRepository(dependencies.config)

        with pytest.raises(ValueError):
            await repo.delete_user("no-such-id")
