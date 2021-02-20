# 2. Testing

## Test Strategies

### Unit Tests

### Integration Tests

Integration Tests exercise several components of your system at once to achieve a desired outcome. They are less specific than unit tests, but they reflect more closely how your end users will interact with the system. When you write requirements for an API, this is usually what you are focused on. You only define what an acceptable outcome would be, not how it is achieved.

Starlette provides a convenient way to write integrations tests with the [TestClient](https://www.starlette.io/testclient/). It simulates an HTTP client request without the need spin up a full server.

In this tutorial I will focus mostly on integration tests. Each section will set out one or more API requirements and I will first set it up as a test case and then continue to implement the necessary system components.

In a real world project each of these components should also be covered by a unit test. This provides you with security and confidence that your do not introduce unintended changes when you work on your code base.

We will see that in our hypothetical API some layers contain little or no logic. Testing their functionality only as part of the system is acceptable in our case.

## Pytest Setup

We will use [Pytest](https://docs.pytest.org/en/stable/) to write our tests so we first need to install it:

```bash
(venv) $ pip install pytest
(venv) $ pip freeze > requirements.txt
```

We will place our tests in a `tests` folder _next_ to the `app` folder. This keeps our production code (`app`) separate from the development code to simplify deployment. Indeed, our Docker image does only contain the `app` code. The test code is only made available via the volume mapping in the `docker-compose.yml` file.

Pytest discovers tests based on the file name. Every file that starts with `test_` is assumed to contain test code. There is no need to match the file structure of the `app` folder but it helps with organizing the tests. We will just add an extra layout to separate integration tests from unit tests.

Setup code for Pytest is held in a `conftest.py` file. The code in the file applies to all tests that are located at the same level or below the level of the `conftest.py` file. You can use more than one setup file, for example to overwrite fixtures with a custom implementation only for a small group of tests.

Taking all of the above we will structure our tests like this:

```
tests
|
└- fixtures (yet to come)
|
└- integration
|  |
|  └- rest
|  |  └- test_healthcheck.py
|  |
|  └- graphql
|
└- unittests (yet to come)
|
└- conftest.py
```

In `conftest.py` we will set up the TestClient instance as a Pytest _fixture_. We also redefine the environment variables that are set up in the `docker-compose.yml` file to have a stable environment for our test runs. This is all the setup we need for now:

```python
# src/tests/conftest.py
import os
import pytest
import re

from starlette.testclient import TestClient

# need to set env var defaults before app is imported
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite://:memory:"
os.environ["TOKEN_SECRET"] = "used to sign tokens"

from app import main

@pytest.fixture(scope="module")
def client():
    with TestClient(main.app) as client:
        yield client
```

I also added a custom `pytest_itemcollected` function which allows a more flexible reporting of the test cases based on the doc string rather than the file name. With this I can add a code to each test that references the requirement for the feature and the test.

## A first test

We already have our `/healthcheck` endpoint. Let's write the requirements for it:

- **[REST-HC-01]** `/healthcheck` returns 200 status
- **[REST-HC-02]** `/healthcheck` reports the environment

These are easy tests to confirm with the test client that we have set up as a fixture:

```python
# tests/integration/rest/test_healthcheck.py
class TestHealthCheckQuery:
    """REST API"""

    def test_healthcheck(self, client):
        """[REST-HC-01] /healthcheck returns 200 status"""
        response = client.get("/healthcheck")
        assert response.status_code == 200

    def test_healthcheck_data(self, client):
        """[REST-HC-02] /healthcheck reports the environment"""
        response = client.get("/healthcheck")
        json = response.json()
        assert json["environment"] == "test"
```

To run the tests locally, use the following command:

```
(venv) $ python -m pytest
```

Or to run the tests within the container use the following commands in the _project root_ folder. The first command is only required once to start the container:

```
$ docker-compose up -d
$ docker-compose exec web python -m pytest
```

The output will be similar to the one show below. Both tests should pass.

```
========================== test session starts ========================
platform darwin -- Python 3.9.1, pytest-6.2.0, py-1.10.0, pluggy-0.13.1
rootdir: .../clean-architecture-python/src, configfile: pytest.ini
collected 2 items

[REST-HC-01] REST API - /healthcheck returns 200 status .        [ 50%]
[REST-HC-02] REST API - /healthcheck reports the environment .   [100%]

=================== 2 passed, 2 warnings in 0.06s =====================
```

Unfortunately, the current stable release of `graphene` uses a deprecated API that will produce some noisy warnings in the output. We can get rid of these by adding a `pytest.ini` file to the `src` folder (not the `tests` folder!):

```
[pytest]
filterwarnings =
    ignore::DeprecationWarning
```

## Testing GraphQL

To test our GraphQL endpoint, we don't need a GraphQL client. We can just send our query as a POST request using the test client. The query is passed to the test client as JSON object:

```python
class TestGraphQLHealthCheckQuery:
    """GraphQL healthcheck"""

    query = "query HealthCheck($name: String) { healthcheck(name: $name) }"

    def test_graphql_healthcheck_response(self, client):
        """[GQL-HC-01] 'healthcheck' returns a default greeting"""
        json = {
            "query": self.query,
        }
        response = client.post("/graphql", json=json)
        result = response.json()

        assert result["data"]["healthcheck"] == "Hello GraphQL!"
```

If we need to pass variables to the query we add them to the JSON object:

```python
    def test_graphql_healthcheck_with_data(self, client):
        """[GQL-HC-02] 'healthcheck' returns a custom greeting with 'name' variable"""
        json = {
            "query": self.query,
            "variables": {"name": "Test"}
        }
        response = client.post("/graphql", json=json)
        result = response.json()

        assert result["data"]["healthcheck"] == "Hello Test!"
```

## Summary

We now have a solid test setup and can continue with the next steps.
