import graphene

from app.domain.users.entities import User as UserEntity


class User(graphene.ObjectType):
    class Meta:
        description = "A User type"

    id = graphene.ID(required=True)
    email = graphene.String(required=True)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    full_name = graphene.String(required=True)

    @staticmethod
    def resolve_full_name(parent: UserEntity, info) -> str:
        return f"{parent.first_name} {parent.last_name}"


class UserProfile(graphene.ObjectType):
    class Meta:
        description = "Details of the current user"

    id = graphene.ID(required=True)
    email = graphene.String(required=True)
    organization_id = graphene.String(required=True)
    is_admin = graphene.Boolean(required=True)
