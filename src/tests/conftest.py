import os
import pytest
import re

from starlette.testclient import TestClient

# need to set env var defaults before app is imported
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite://:memory:"
os.environ["TOKEN_SECRET"] = "used to sign tokens"

from app import main


SPEC_REGEX = re.compile(r"\s?\[\D+-\d+\]\s?")


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
