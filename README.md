# Clean Architecture in Python

In this repo I will build up a GraphQL server in Python based on [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) principles. This is mostly an academic exercise without a specific application in mind. I hope that the insights gained here will help me when next I have to think about real world programming problems.

## Table of Contents

0. Introduction (yet to come)
1. [Basic FastAPI server with GraphQL in Docker](./src/docs/01_fastapi_graphql_docker.md)
2. [Testing](./src/docs/02_testing.md)
3. [Dependency Injection](./src/docs/03_dependency_injection.md)
4. The first Use Case

- a) [Domain Entities](./src/docs/04a_entities.md)
- b) [UserRepository Interface](./src/docs/04b_repository_interface.md)
- c) [In-Memory UserRepository Implementation](./src/docs/04c_memory_repository.md)
- d) [UserService](./src/docs/04d_user_service.md)
- e) [Use Case Logic](./src/docs/04e_list_users_use_case.md)
- f) [GraphQL Resolvers](./src/docs/04f_query_users_resolver.md)

5. [Dependency Injection Redux](./src/docs/05_di_redux.md)

6. Authentication

- a) [Authentication Token](./src/docs/06a_authentication.md)
- b) [Authentication Middleware](./src/docs/06b_auth_middleware.md)

7. Groups and Resources
8. Memberships
9. Permissions

## Installation

In the _repo root folder_ ('clean-architecture-python') run

```
$ docker-compose up -d --build
```

This will build and start the Docker image. You can test that it's running with `curl`:

```
$ curl http://localhost:4000/healthcheck
```

### Testing

First start the container, then use a Docker command to run Pytest within the container:

```
$ docker-compose up -d
$ docker-compose exec web python -m pytest
```

### Development

The `src` folder is a mapped volume in the Docker container and the startup command runs `uvicorn` with the `--reload` option so a change to the source files will restart the server automatically.

However, Python dependencies are installed only in the container and not accessible by your editor. Your editor may depend on these to enable things like Intellisense. You can create a virtual environment in the `src` folder for the editor and to run the server script outside of the docker container:

```bash
$ cd src
$ python3.9 -m venv ./venv
$ source ./venv/bin/activate
$ pip install -r requirements.txt
```

The you can start the server _in the src folder_ with these commands:

```bash
$ source ./venv/bin/activate
$ uvicorn app.main:app --reload
```

In later steps the server requires environment variables to be set. You can define a set of variables in an `env` file and load it with the `source` command:

```bash
$ source ./venv/bin/activate
$ source ./env.test
$ uvicorn app.main:app --reload
```

If you use VS Code you can also use a [Remote Python Development](https://devblogs.microsoft.com/python/remote-python-development-in-visual-studio-code/).
