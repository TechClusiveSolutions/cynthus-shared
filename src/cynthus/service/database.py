"""Async access to a service's database for the Cynthus project"""

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from .database_target import DatabaseTarget
from .database_url import DatabaseUrl


class Database:
    """Creates engines on first use, so importing the service never needs a database.

    ``session()`` uses the default engine (``DB_*``, or the ``url`` given). ``engine(target)`` and ``get_session(env,
    service)`` reach any of the environments of ``DatabaseTarget``; there is one cached engine per target.
    """

    def __init__(self, url=None) -> None:
        self._url = url
        self._engine: AsyncEngine | None = None
        self._sessions: async_sessionmaker[AsyncSession] | None = None
        self._targets: dict[DatabaseTarget, tuple[AsyncEngine, async_sessionmaker[AsyncSession]]] = {}

    def session(self) -> AsyncSession:
        return self._default()[1]()

    def engine(self, target: DatabaseTarget | None = None) -> AsyncEngine:
        """The cached engine of the target, or the default engine when none is given."""

        if target is None:
            return self._default()[0]

        return self._connect(target)[0]

    def get_session(self, env: str | None, service: str) -> AsyncSession:
        """A session on the service's database and schema for ``env``, normally ``environ.get('ENV')``.

        An unset environment means development; an unknown one raises ``ValueError``.
        """

        target = DatabaseTarget.resolve(env, service)

        return self._connect(target)[1]()

    async def dispose(self) -> None:
        engines = [engine for engine, _ in self._targets.values()]

        if self._engine is not None:
            engines.append(self._engine)

        for engine in engines:
            await engine.dispose()

        self._engine = None
        self._sessions = None
        self._targets = {}

    def _default(self) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
        if self._sessions is None:
            self._engine = create_async_engine(self._url or DatabaseUrl().build(), pool_pre_ping=True)
            self._sessions = async_sessionmaker(self._engine, expire_on_commit=False)

        return self._engine, self._sessions

    def _connect(self, target: DatabaseTarget) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
        if target not in self._targets:
            options = {'connect_args': {'options': f'-csearch_path={target.schema}'}} if target.schema else {}
            engine = create_async_engine(target.url, pool_pre_ping=True, **options)
            self._targets[target] = (engine, async_sessionmaker(engine, expire_on_commit=False))

        return self._targets[target]
