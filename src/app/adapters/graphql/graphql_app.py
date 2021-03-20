import graphene
import starlette.graphql

from graphql.execution.executors.asyncio import AsyncioExecutor

from .mutation import Mutation
from .query import Query

schema = graphene.Schema(mutation=Mutation, query=Query)


class GraphQLApp(starlette.graphql.GraphQLApp):
    def __init__(self, *args, **kwargs):
        starlette.graphql.GraphQLApp.__init__(
            self,
            schema=schema,
            executor_class=AsyncioExecutor,
            *args,
            **kwargs,
        )
