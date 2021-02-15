# 3. Dependency Injection

## Overview

Dependency Injection is an essential element for Clean Architecture. It enables us to set up runtime dependencies in the outer level and pass them on to classes in the inner layers where they are needed.

In our example app, the business logic is implemented by _Use Cases_ at the core of our domain. Each use case depends on one or more _Services_ (also part of the core). Each service depends on a _Repository_ which is implemented in the outer layer based on a specific storage technology.

While we can use _Interfaces_ to reverse the dependency of code we still need a mechanism to provide an instance of such an interface (repository) to the instance that depends on it (service/use case). A _Dependency Injection_ framework is such a mechanism.

## Setup

For our project we will use the [Dependency Injector](https://python-dependency-injector.ets-labs.org/) framework. First of all, we need to install it:

```
(venv) $ pip install dependency-injector
(venv) $ pip freeze > requirements.txt
```

### Defining Dependencies

We don't have any class yet that require dependencies. So for the moment we will just set up a basic configuration provider. When we implement our repositories and services we can add to this setup as needed.

Our dependencies will all be contained in the `AppDependencies` class. We can set up several containers (like `Core`) and assemble them inside `AppDependencies`. Additionally, we create an instance of a `Configuration` provider to pass configuration options to all dependencies that might require them.

With _Dependency Injector_ the pattern is usually to set up a base dependency and then to overwrite individual values as needed. To create our configuration, we first set up the `config` instance and then load a template (`base_configuration`) from a dictionary. This template contains default values and placeholders that we need to replace during runtime. Here we expect the values for `DATABASE_URL`, `ENVIRONMENT` and `TOKEN_SECRET` to be replaced by values from the environment. Because these are security sensitive I have made them `required` so an exception will be raised if they are not provided.

The complete `config` object is then passed as option to the `Core` provider when the relevant configuration sections are used to set up logging options. Likewise, the configured database url can be used to set up a database client instance.

```python
# src/app/di_containers.py
import logging.config
from dependency_injector import containers, providers

from app.config import base_configuration

class Core(containers.DeclarativeContainer):
    config = providers.Configuration()
    logging = providers.Resource(
        logging.config.dictConfig,
        config=config.logging,
    )

class AppDependencies(containers.DeclarativeContainer):

    config = providers.Configuration()
    config.from_dict(base_configuration)

    # override config with environment variables
    config.database.url.from_env("DATABASE_URL", required=True)
    config.environment.from_env("ENVIRONMENT", required=True)
    config.services.auth.secret.from_env("TOKEN_SECRET", required=True)

    core = providers.Container(
        Core,
        config=config.core,
    )
```

### Using the Dependency Container

Import the new `AppDependencies` container, create an instance and initialize the dependencies with a call to `dependencies.core.init_resources()`. For the moment this is all we need to do. But once we have classes that require a dependency injected in our code we have to make the framework aware of these classes to the required instances can be provided at run time. We will cover this with the addition of our repositories and services.

We don't yet have a class that requires dependency injection so to confirm that the dependencies are set up properly we replace `os.getenv` with `dependencies.config.environment()` to get the environment.

```python
# src/app/main.py
from fastapi import FastAPI
from app.adapters.graphql.graphql_app import GraphQLApp

from app.di_containers import AppDependencies

dependencies = AppDependencies()
dependencies.core.init_resources()
# TODO: dependency discovery

app = FastAPI()

@app.get("/healthcheck")
async def healthcheck():
    return {
        "ping": "pong",
        "environment": dependencies.config.environment(),
    }
```

When you run the server now and query the `/healthcheck` REST endpoint you will see that `environment` in `dependencies.config` has been replaced with the value from the environment variable. It is now 'development' and no longer the empty string set up in the config template file.

#### src/tests/conftest.py

To add our dependencies to the test cases we can use another Pytest fixture. Before we can import `AppDependencies` we need to set up the required environment variable or the import will fail.

Then we can define a `dependencies` fixture where we create and initialize the instance. The scope of this fixture can be broad (`session`) because once set up the dependencies will not change. If you plan to test your code under different environments or with different adapters you can set up multiple dependency fixtures.

Finally we make the `dependencies` fixture a dependency of the `client` fixture. We won't explicitly use it but having it as a dependency will run the setup code before the `client` fixture is used. So all dependencies will be in place when we run our tests.

```python
import os
import pytest
import re

from starlette.testclient import TestClient

# need to set environment before AppDependencies or app are imported
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite://:memory:"
os.environ["TOKEN_SECRET"] = "used to sign tokens"

from app import main
from app.di_containers import AppDependencies

@pytest.fixture(scope="session")
def dependencies():
    dependencies = AppDependencies()
    dependencies.core.init_resources()
    # TODO: dependency discovery

    yield dependencies

@pytest.fixture(scope="module")
def client(dependencies):
    with TestClient(main.app) as client:
        yield client
```

You can run the tests now to confirm that everything still works and that the `ENVIRONMENT` is set to `test` as required by the test. To prove that the value is provided via the set up dependencies you can modify the value in the `conftest.py` file and see the test fail.

## Next Steps

We have our Dependency Injection framework in place. When we implement use cases in the next chapter, we will extend it to provide repositories to services and services to use cases. This makes the use case and services code (inner layer) independent from the repositories (outer layer).
