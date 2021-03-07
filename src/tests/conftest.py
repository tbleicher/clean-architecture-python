import os
import pytest
import re

from starlette.testclient import TestClient

# need to set environment before AppDependencies or app are imported
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite://:memory:"
os.environ["TOKEN_SECRET"] = "used to sign tokens"

from app.adapters.repositories.utils import load_fixtures
from app import main
from app.di_containers import AppDependencies

SPEC_REGEX = re.compile(r"\s?\[\D+-\d+\]\s?")

fixtures = {
    "users": "tests/fixtures/users.json",
}


@pytest.fixture(scope="session")
def all_users():
    data = load_fixtures(fixtures["users"])
    yield data


@pytest.fixture(scope="session")
def dependencies():
    dependencies = AppDependencies()
    dependencies.init_resources()
    dependencies.config.repositories.fixtures.from_dict(fixtures)
    # TODO: dependency discovery

    yield dependencies


@pytest.fixture(scope="module")
def client():
    with TestClient(main.app) as client:
        yield client


def get_spec_id(prefix: str = "", description: str = "") -> str:
    """look for a requirement id and return id and description as tuple"""
    match = SPEC_REGEX.search(description)
    if not match:
        return " - ".join([prefix, description])

    spec = match.group().strip()
    desc = " ".join(SPEC_REGEX.split(description)).strip()
    text = " - ".join([prefix, desc])

    return f"{spec} {text}"


def pytest_itemcollected(item):
    """format test output based on doc strings in test files"""
    par = item.parent.obj
    node = item.obj
    prefix = par.__doc__.strip() if par.__doc__ else par.__class__.__name__
    suffix = node.__doc__.strip() if node.__doc__ else node.__name__

    if prefix or suffix:
        item._nodeid = get_spec_id(prefix, suffix)
