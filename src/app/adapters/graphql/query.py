import graphene

from . import resolvers
from . import types


class Query(graphene.ObjectType):

    healthcheck = graphene.String(name=graphene.String(default_value="GraphQL"))

    profile = graphene.Field(types.UserProfile)

    users = graphene.List(graphene.NonNull(types.User), required=True)

    @staticmethod
    def resolve_healthcheck(parent, info, name):
        return f"Hello {name}!"

    @staticmethod
    async def resolve_profile(parent, info):
        return await resolvers.get_user_profile(info)

    @staticmethod
    async def resolve_users(parent, info):
        return await resolvers.list_users()
