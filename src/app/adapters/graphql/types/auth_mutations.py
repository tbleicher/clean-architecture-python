import graphene

from app.domain.auth.entities import TokenDataDTO

from .. import resolvers
from .auth import LoginInput, TokenData


class LoginMutation(graphene.Mutation):
    class Arguments:
        input = LoginInput(required=True)

    Output = graphene.NonNull(TokenData)

    @staticmethod
    async def mutate(parent, info, input: LoginInput) -> TokenData:
        data: TokenDataDTO = await resolvers.login(input)
        return TokenData(token=data.token)
