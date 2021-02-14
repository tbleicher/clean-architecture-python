import os
from fastapi import FastAPI
from app.adapters.graphql.graphql_app import GraphQLApp

app = FastAPI()


@app.get("/healthcheck")
async def healthcheck():
    return {
        "ping": "pong",
        "environment": os.getenv("ENVIRONMENT"),
    }


app.add_route("/graphql", GraphQLApp())
