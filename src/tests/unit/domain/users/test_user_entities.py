import pytest
from pydantic import ValidationError

from app.domain.users.entities import User

user_data = {
    "id": "EX-001",
    "email": "ex1@example.com",
    "first_name": "First",
    "last_name": "Last",
    "organization_id": "Org",
    "is_admin": False,
}


class TestUserEntity:
    """domain.entities.user"""

    def test_user_from_named_arguments(self):
        """[DOM-ENT-US-01] user can be created from named arguments"""
        user = User(**user_data)

        assert user.id == user_data["id"]
        assert user.email == user_data["email"]

    def test_user_from_dictionary(self):
        """[DOM-ENT-US-02] user can be created from dictionary"""
        user = User.parse_obj(user_data)

        assert user.id == user_data["id"]
        assert user.email == user_data["email"]

    def test_user_from_existing_user(self):
        """[DOM-ENT-US-03] user can be created from an existing user"""
        user1 = User.parse_obj(user_data)
        user2 = User.parse_obj({**user1.dict(), "id": "EX-002"})

        assert user2.id == "EX-002"
        assert user2.email == user_data["email"]

    def test_user_from_dict_with_missing_arguments(self):
        """[DOM-ENT-US-04] all arguments are required"""
        data = {**user_data}
        del data["email"]

        with pytest.raises(ValidationError):
            user = User.parse_obj(data)

    def test_user_from_dict_with_extra_arguments(self):
        """[DOM-ENT-US-05] extra constructor arguments are ignored"""
        data = {**user_data, "extra": "unused value"}
        user = User.parse_obj(data)

        assert user.id == user_data["id"]

        with pytest.raises(KeyError):
            user.dict()["extra"]

    def test_data_types_are_enforced(self):
        """[DOM-ENT-US-06] argument data types are enforced"""
        with pytest.raises(ValidationError):
            user = User(**{**user_data, "is_admin": "not_bool"})

    def test_user_instance_is_immutable(self):
        """[DOM-ENT-US-07] user instance is immutable"""
        user = User(**user_data)

        with pytest.raises(TypeError):
            user.id = "EX-002"
