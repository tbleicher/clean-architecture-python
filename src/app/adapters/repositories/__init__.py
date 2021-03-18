from dependency_injector import containers, providers


from .users.memory_user_repository import MemoryUserRepository


class MemoryRepositories(containers.DeclarativeContainer):

    config = providers.Configuration()

    user_repository = providers.Singleton(
        MemoryUserRepository,
        config=config,
    )
