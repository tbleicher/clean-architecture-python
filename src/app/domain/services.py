from dependency_injector import containers, providers


from .users.service import UserService


class Services(containers.DeclarativeContainer):

    repositories = providers.DependenciesContainer()

    user_service = providers.Factory(
        UserService,
        repository=repositories.user_repository,
    )
