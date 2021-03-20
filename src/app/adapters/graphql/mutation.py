import graphene

from . import types


class Mutation(graphene.ObjectType):
    login = types.LoginMutation.Field()
