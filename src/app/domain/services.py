from dependency_injector import containers, providers

from .auth.service import AuthService
from .users.service import UserService


class Services(containers.DeclarativeContainer):

    config = providers.Configuration()

    repositories = providers.DependenciesContainer()

    auth_service = providers.Factory(
        AuthService,
        repository=repositories.user_repository,
        config=config.services.auth,
    )

    user_service = providers.Factory(
        UserService,
        repository=repositories.user_repository,
    )
