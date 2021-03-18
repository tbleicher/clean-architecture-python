# 5. Dependency Injection Redux

## The Problem

In the previous chapter we defined the `list_users` GraphQL resolver like this:

```python
from app.domain.users.use_cases import ListUsersUseCase
from app.adapters.repositories.users.memory_user_repository import MemoryUserRepository
from app.domain.users.service import UserService

config_with_users = {
    # ... config values
}

async def list_users() -> List[User]:
    """call use case and convert user entities to GraphQL Users"""
    tmp_user_repo = MemoryUserRepository(config=config_with_users)
    tmp_user_service = UserService(repository=tmp_user_repo)

    use_case = ListUsersUseCase(user_service=tmp_user_service)
    return await use_case.execute()
```

We need to import configuration, repository and service and create instances of the repository and the service just to be able to create an instance of the `ListUsersUseCase`. This feels cumbersome and repetitive and will become a maintenance issue when our app grows and we require a lot of use cases.

Wouldn't it be great if there was a sufficiently advanced technology that would allow us to just write the last two lines? Well, let me tell you: _Dependency Injection_ is this piece of magic.

## How it works

With our [Dependency Injector](https://python-dependency-injector.ets-labs.org/) framework we define a container with dependencies. A dependency is represented as a _Provider_. Providers are class factories that know which dependencies are required to create a new instance of a class. When we request an instance, the framework will inject the dependencies in the constructor and return a new instance.

Where we want to use one these dependencies, we have to place a `Provide` marker in the constructor function and decorate it with an `@inject` decorator. At startup the framework will inspect the code and look for these markers. Where one is found, the required dependency is replaced with the defined factory.

If we now create a new instance of the class that has dependencies injected the framework will provide an instance of the dependency as constructor argument and we don't need to manage it ourselves.

In our code, we will use _Dependency Injection_ to provide dependencies for our use cases. The use case constructors will hold the markers for the dependencies (services) the use case requires. We then set up a _Container_ for our repositories and one for our services. In the main _AppDependencies_ container we will then link them together to resolver the dependency chain.

We could continue on and set up a DI container for our use cases as well. But while there are a handful of services are are dozens and dozens of use cases so setting up the container will be tedious. There is also little to gain because it is perfectly fine to import a use case directly into our resolvers. We would probably do that anyway just for the typing support.

## Repositories

Let's begin with the dependency container for the repositories. In this container we will set up all repositories with their dependencies. You can use a dedicated `di_container.py` file for this but I chose to set up the container in the `__init__.py` file of the `repositories` folder. In the end this will be our only export from this folder, so it seems to be the appropriate place.

```python
# src/app/adapters/repositories/__init__.py
from dependency_injector import containers, providers

from .users.memory_user_repository import MemoryUserRepository

class MemoryRepositories(containers.DeclarativeContainer):

    config = providers.Configuration()

    user_repository = providers.Singleton(
        MemoryUserRepository,
        config=config,
    )
```

A container is defined by sub-classing `containers.DeclarativeContainer` from the `dependency_injector` package. Then we have to define placeholders for dependencies that our repo instances might need. For the in-memory repository this is just a `config` instance. Other implementations (like SQL based repos) might also have dependencies on a database connection or similar. In that case we would have to define suitable placeholders as well.

The `config` placeholder is defined as an empty configuration instance. At runtime this `config` will be replaced by the `config` instance set up in `AppDependencies` so we do not have to provide any default values.

Then we can set up a name for our `MemoryUserRepository` factory. I call it `user_repository` and we will reference it as `<container>.user_repository` when we define it as a dependency.

Our repository factory is set up as a _Singleton_ instance. The DI framework provides this factory option for classes that should only have one instance in the entire app. This is what we want for the repository because we initialise our internal `_users` hash and load fixture in the constructor and we only want to do this once. Otherwise we could create a new user in one request and would be gone in the next because the storage has been reset.

When the factory wants to create an instance of the repository it has to provide a `config` argument. We define it as extra arguments to the Singleton constructor and set it to the `config` placeholder that we defined within the container. When the instance is created, this `config` instance will hold the values we set up and extend via the `AppDependencies` container.

## Services

In the same way we can set up service factories in our `domain` folder. We don't need a `config` object for our services (yet) but we do need instances of our repositories. We an set up a `repositories` placeholder like before to replace it with the real repository factories container at run time.

Now we can set up a `user_service` factory based on our `UserService` class. This time we use the `providers.Factory` class because the service itself has no setup to speak of. This means that every use case instance will receive a dedicated instance of the service. If we wanted to maintain some internal state we would have to use a different option like the `Singleton`.

```python
# src/app/domain/services.py
from dependency_injector import containers, providers

from .users.service import UserService

class Services(containers.DeclarativeContainer):

    repositories = providers.DependenciesContainer()

    user_service = providers.Factory(
        UserService,
        repository=repositories.user_repository,
    )
```

The service requires a user repository instance as `repository` argument. We have this repository type set up as `user_repository` in the `MemoryRepositories` container. At runtime, this container will replace the local `repositories` placeholder. Therefore we can declare our dependency with `repository=repositories.user_repository`.

## App Dependencies

To bring it all together we import the two containers into our `AppDependencies` setup:

```python
# src/app/di_containers.py
from dependency_injector import containers, providers

from app.config import base_configuration
from app.adapters.repositories import MemoryRepositories
from app.domain.services import Services

class AppDependencies(containers.DeclarativeContainer):

    config = providers.Configuration()
    config.from_dict(base_configuration)

    # override config with environment variables
    config.database.url.from_env("DATABASE_URL", required=True)
    config.environment.from_env("ENVIRONMENT", required=True)
    config.services.auth.secret.from_env("TOKEN_SECRET", required=True)

    repositories = providers.Container(
        MemoryRepositories,
        config=config,
    )

    services = providers.Container(
        Services,
        repositories=repositories,
    )
```

We have set up the `repositories` as an instance of the `MemoryRepository` container. The `config` placeholder defined in it is going to be replaced by the `config` object we have defined here and so it will hold all values from the base config and the environment variable.

Then we define the `services` container and replace the `repositories` placeholder with our in-memory repository instances. If some of our services need access to the configuration as well we could just pass it in here in the same way.

Note that we could set up another repository container, for example with SQL based repositories. All we would need to do to replace the repository implementation for the entire app is to set them up as the `repositories` dependency in this file.

## Use Case Wiring

All dependencies are set up and ready to use. We now have to inject them as constructor arguments into our use cases. In our framework this is called the _wiring_.

First we need to identify functions that needs to be processed during the dependency discovery. For this the framework provides the `inject` decorator which we need to add to our `__init__` method.

Then we have to declare which dependency we want to inject using the `Provide` marker. `Provide` will give us an instance of the specified dependency. In this case it's the user service at `AppDependencies.services.user_service`.

Note that I have added a `# type: ignore` comment to the dependency declaration. Python's typing system does not accept the `Provide` marker as a valid instance for the `UserServiceInterface` and will highlight this line as an error.

```python
# src/app/domain/users/use_cases/list_users.py
from typing import List
from dependency_injector.wiring import inject, Provide

from app.di_containers import AppDependencies

from ..entities import User
from ..interfaces import UserServiceInterface

class ListUsersUseCase:
    """return list of users"""

    @inject
    def __init__(
        self,
        user_service: UserServiceInterface = Provide[AppDependencies.services.user_service],  # type: ignore
    ):
        self.user_service = user_service

    async def execute(self) -> List[User]:
        return await self.user_service.find_all()

```

> Importing `AppDependencies` may look like a violation of our domain boundaries. But just because the dependencies are not defined inside of the `domain` folder does not mean they are not part of the domain code.

We only need to place markers in our Use Case code. The internal dependencies for repositories and configuration are already taken care of in the container setup.

## Dependency Discovery

The final step to implement our dependencies is link our providers to the markers. Our dependency container has a `wire` method to do this. The only place where we use markers is in the `domain` folder. We can import it and pass it to `wire` as a _package_. The DI framework will now search through all the file in the folder for dependency markers and replace them with the services we set up.

```python
# src/app/main.py
# ...
from app.di_containers import AppDependencies
from app import domain

dependencies = AppDependencies()
dependencies.init_resources()

# dependency discovery
dependencies.wire(packages=[domain])

# ...
```

We need to make the same change in `conftest.py` where we set up the dependencies for our test cases. To make sure that the dependencies are in place before we make a call with our test client I added the `dependencies` fixture as a dependency for the `client` fixture.

```python
# tests/conftest.py
#...

from app import domain

@pytest.fixture(scope="session")
def dependencies():
    dependencies = AppDependencies()
    dependencies.init_resources()
    dependencies.config.repositories.fixtures.from_dict(fixtures)
    # dependency discovery
    dependencies.wire(packages=[domain])

    yield dependencies


@pytest.fixture(scope="module")
def client(dependencies):
    with TestClient(main.app) as client:
        yield client
```

## Resolver cleanup

The dependencies and their wiring is in place now. We can put it to the test and remove the temporary resolver and service definitions from our `list_user` resolver:

```python
async def list_users() -> List[User]:
    """call use case and convert user entities to GraphQL Users"""
    use_case = ListUsersUseCase()
    return await use_case.execute()
```

When the resolver is called it creates a `ListUsersUseCase` instance but does not provided the required UserService instance. We expect that our dependency injection framework will take care of it. To verify this we can run our users query integration test:

`(venv) $ python -m pytest -k test_query_users_list`

This test should still pass and prove that our dependencies are injected where we need them.

## Dev Fixtures

One last update to improve our development setup is an option to load fixture into the app itself, and not only for unit tests. We can copy the fixture code from `conftest.py` but add an extra condition to trigger the loading of the configured fixture files.

Now we can start the app from the command line and should have fixtures available to query provided that:

- the `LOAD_FIXTURES` environment variable is set to **"true"**
- the `ENVIRONMENT` environment variable is set to **"test"**

```python
# src/app/main.py
# ...

fixtures = {
    "users": "tests/fixtures/users.json",
}

dependencies = AppDependencies()
dependencies.init_resources()

# load fixtures based on environment
if os.environ.get("LOAD_FIXTURES", "") == "true":
    dependencies.config.repositories.fixtures.from_dict(fixtures)

# dependency discovery
dependencies.wire(packages=[domain])

app = FastAPI()
# ...
```

## Summary and Recap

Now the basic blueprint for our Clean Architecture GraphQL service is complete. To add new features to our service we will repeat the steps for the `users` resolver and

1. define a _Repository_ to store data records and create entities from the records
2. define a _Service_ to interface with the repository
3. add the repository and service to our _dependencies_
4. define a UseCase for every user interaction with the data
5. define a GraphQL type to represent the entity in the Schema
6. define a schema endpoint and resolver to call the use case

Feel free to exercise these steps by adding 'groups' and 'resources' to the service. We will use them later on.

For now we are limited to listing users. Before we can add any proper logic to our use cases we need to implement a way to authenticate a user. Only when we know who is making a request we can add further logic to limit and filter the results that the user should see. This will be the topic of our next chapter.
