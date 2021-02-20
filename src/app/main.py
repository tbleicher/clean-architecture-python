from fastapi import FastAPI
from app.adapters.graphql.graphql_app import GraphQLApp

from app.di_containers import AppDependencies

dependencies = AppDependencies()
dependencies.init_resources()
# TODO: dependency discovery


app = FastAPI()


@app.get("/healthcheck")
async def healthcheck():
    return {
        "ping": "pong",
        "environment": dependencies.config.environment(),
    }


app.add_route("/graphql", GraphQLApp())
