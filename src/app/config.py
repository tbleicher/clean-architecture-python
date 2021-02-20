base_configuration = {
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
