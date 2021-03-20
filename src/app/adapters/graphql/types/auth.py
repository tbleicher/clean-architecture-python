import graphene


class LoginInput(graphene.InputObjectType):
    class Meta:
        description = "data required for a login request"

    email = graphene.String(required=True)
    password = graphene.String(required=True)


class TokenData(graphene.ObjectType):
    class Meta:
        description = "data returned after a successful login"

    token = graphene.String(required=True)
