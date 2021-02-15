base_configuration = {
    "core": {
        "logging": {
            "version": 1,
            "formatters": {
                "formatter": {
                    "format": "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
                }
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "formatter",
                "stream": "ext://sys.stderr",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["console"]},
    },
    "database": {
        "url": "sqlite://:memory:",
    },
    "environment": "",
    "repositories": {"fixtures": {}},
    "services": {
        "auth": {
            "algorithm": "HS256",
            "secret": "this must be overridden by env variable",
            "token_ttl": 3600,
        }
    },
}
