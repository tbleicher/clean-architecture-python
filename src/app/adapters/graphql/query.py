import graphene


class Query(graphene.ObjectType):

    healthcheck = graphene.String(name=graphene.String(default_value="GraphQL"))

    @staticmethod
    def resolve_healthcheck(parent, info, name):
        return f"Hello {name}!"
