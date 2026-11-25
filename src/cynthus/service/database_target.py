"""Where a service's database lives for one environment: the connection URL and the schema."""

import re
from collections.abc import Mapping
from dataclasses import dataclass
from os import environ

from sqlalchemy import URL

from .database_url import DatabaseUrl

PRODUCTION = 'production'
TESTING = 'testing'
DEVELOPMENT = 'development'

# The prefix of the environment variables that configure each environment: DB_*, TEST_DB_* and DEV_DB_*.
PREFIXES = {PRODUCTION: '', TESTING: 'TEST_', DEVELOPMENT: 'DEV_'}

# Names that are safe to put in a search_path and in a schema name.
NAME = re.compile(r'[a-z_][a-z0-9_]*')


@dataclass(frozen=True)
class DatabaseTarget:
    """The database a service uses in one environment, so one container can run against a copy of the data.

    ``DatabaseTarget.resolve(env, service)`` reads ``DB_*`` for production, ``TEST_DB_*`` for testing and ``DEV_DB_*``
    for development (HOST, PORT, NAME, USERNAME, PASSWORD and an optional SCHEMA). Switching copies is changing ``ENV``.
    """

    url: URL
    schema: str | None = None

    @classmethod
    def resolve(cls, env: str | None, service: str, environment: Mapping[str, str] | None = None) -> 'DatabaseTarget':
        """Resolve the target for ``env`` (production, testing or development; none means development).

        The schema is ``<prefix>DB_SCHEMA`` when set, otherwise the service name, or ``test_<service>`` when testing.
        An unknown environment, a bad service name or a missing required variable raises ``ValueError``.
        """

        values = environ if environment is None else environment
        name = (env or DEVELOPMENT).strip().lower()

        if name not in PREFIXES:
            raise ValueError(f'Unknown environment {env!r}; expected one of {", ".join(PREFIXES)}')

        if not NAME.fullmatch(service):
            raise ValueError(f'Invalid service name {service!r}; use lower case letters, digits and underscores')

        prefix = PREFIXES[name] + 'DB_'
        missing = [prefix + key for key in ('NAME', 'USERNAME', 'PASSWORD') if not values.get(prefix + key)]

        if missing:
            raise ValueError(f'The {name} database needs {", ".join(missing)} in the environment')

        mapped = {
            f'DB_{key}': values[prefix + key] for key in ('HOST', 'PORT', 'NAME', 'USERNAME', 'PASSWORD')
            if values.get(prefix + key)
        }

        default = f'test_{service}' if name == TESTING else service
        schema = values.get(prefix + 'SCHEMA') or default

        if not NAME.fullmatch(schema):
            raise ValueError(f'Invalid schema name {schema!r}; use lower case letters, digits and underscores')

        return cls(DatabaseUrl(mapped).build(), schema)
