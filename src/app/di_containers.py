from dependency_injector import containers, providers

from app.config import base_configuration

from app.adapters.repositories import MemoryRepositories
from app.domain.services import Services


class AppDependencies(containers.DeclarativeContainer):

    config = providers.Configuration()
    config.from_dict(base_configuration)

    # override config with environment variables
    config.database.url.from_env("DATABASE_URL", required=True)
    config.environment.from_env("ENVIRONMENT", required=True)
    config.services.auth.secret.from_env("TOKEN_SECRET", required=True)

    repositories = providers.Container(
        MemoryRepositories,
        config=config,
    )

    services = providers.Container(
        Services,
        config=config,
        repositories=repositories,
    )
