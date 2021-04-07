import logging
import os

from fastapi import FastAPI, Request

from app.adapters.graphql.graphql_app import GraphQLApp
from app.adapters.http.middleware import get_token_user
from app.di_containers import AppDependencies
from app import domain


fixtures = {
    "users": "tests/fixtures/users.json",
}

dependencies = AppDependencies()
dependencies.init_resources()

# load fixtures based on environment
if os.environ.get("LOAD_FIXTURES", "false") == "true":
    dependencies.config.repositories.fixtures.from_dict(fixtures)

# dependency discovery
dependencies.wire(packages=[domain])


app = FastAPI()


@app.middleware("http")
async def session(request: Request, call_next):
    try:
        request = await get_token_user(request)
    except Exception as exc:
        logging.error(exc)

    response = await call_next(request)
    return response


@app.get("/healthcheck")
async def healthcheck():
    return {
        "ping": "pong",
        "environment": dependencies.config.environment(),
    }


app.add_route("/graphql", GraphQLApp())
