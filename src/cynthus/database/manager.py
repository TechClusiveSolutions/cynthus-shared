"""Database Manager class for the Cynthus project"""

import functools
import logging

from contextlib import contextmanager
from os import environ
from sqlalchemy import create_engine
from time import sleep
from typing import Callable, Optional, TypeVar

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker, scoped_session

from cynthus.core.model import Base


class DatabaseManager:
    default_db: str = environ.get('DB_NAME')
    default_env: str = environ.get('ENV')
    sessions: dict[str, Callable[[], Session]] = {}
    engines: dict[str, Engine] = {}


    @classmethod
    def get_scoped_factory(cls,
        db: Optional[str] = None,
        env: Optional[str] = None,
        config: Optional[dict] = None
    ) -> scoped_session:
        """Returns a scoped session factory for the given database and environment"""

        logger = logging.getLogger(__name__)
        this_db = db or cls.default_db
        this_env = env or cls.default_env
        key = f'{this_db}:{this_env}'

        if key in cls.sessions:
            return cls.sessions[key]

        try:
            engine = cls.get_engine(this_db, this_env, config)

            params = {
                'bind': engine,
                'autocommit': False,
                'autoflush': False,
            }

            factory = sessionmaker(**params)
            ss = scoped_session(factory)

            cls.sessions[key] = ss
        except Exception as error:
            logger.error('Could not create a scoped database session factory for %s: %s', key, str(error))

        return cls.sessions[key]


    @classmethod
    def get_scoped_session(cls,
        db: Optional[str] = None,
        env: Optional[str] = None,
        config: Optional[dict[str, str]] = None
    ) -> Optional[Session]:
        """Returns a scoped database session for the given database and environment"""

        logger = logging.getLogger(__name__)
        factory = cls.get_scoped_factory(db, env, config)

        if factory is None:
            return factory

        return factory()


    @classmethod
    def get_engine(cls,
        db: Optional[str] = None,
        env: Optional[str] = None,
        config: Optional[dict[str, str]] = None
    ) -> Optional[Engine]:
        """Returns a database engine object for the given database and environment"""

        logger = logging.getLogger(__name__)
        this_db = db or cls.default_db
        this_env = env or cls.default_env
        key = f'{this_db}:{this_env}'

        if key in cls.engines:
            logger.debug('Found an existing engine for %s: using engine', key)

            return cls.engines[key]

        try:
            logger.debug('No engine found for %s: creating engine', key)

            dsn, args = cls._get_dsn(this_db, this_env, config)

            params = {
                'pool_size': 10,
                'max_overflow': 20,
                'pool_recycle': 3600,
                'pool_pre_ping': True,
                **args
            }

            cls.engines[key] = create_engine(dsn, ** params)

            logger.info('Created database engine for %s', key)
        except Exception as error:
            logger.error('Could not create database engine for %s: %s', key, str(error))

        return cls.engines[key]


    @classmethod
    def _get_dsn(cls,
        db: Optional[str] = None,
        env: Optional[str] = None,
        config: Optional[dict[str, str]] = None
    ) -> Optional[str]:
        """Returns a formatted DSN for the given database and environment"""

        logger = logging.getLogger(__name__)
        this_db = db or cls.default_db
        this_env =env or cls.default_env

        if config is None:
            logger.info('No config specified: reading database configuration from the environment')

            driver = environ.get(f'DB_DRIVER_{this_db}_{this_env}')
            host = environ.get(f'DB_HOST_{this_db}_{this_env}')
            port = environ.get(f'DB_PORT_{this_db}_{this_env}')
            dbname = environ.get(f'DB_NAME_{this_db}_{this_env}')
            username = environ.get(f'DB_USERNAME_{this_db}_{this_env}')
            password = environ.get(f'DB_PASSWORD_{this_db}_{this_env}')
            options = environ.get(f'DB_OPTIONS_{this_db}_{this_env}')
        else:
            logger.info('Reading database configuration from config')

            driver = config.get('driver')
            host = config.get('host')
            port = config.get('port')
            dbname = config.get('dbname')
            username = config.get('username')
            password = config.get('password')
            options = config.get('options')

        dsn = '{}://{}:{}@{}:{}/{}'.format(
            driver,
            username,
            password,
            host,
            port,
            dbname
        )

        return dsn, options


@contextmanager
def db_context(
    db: Optional[str] = None,
    env: Optional[str] = None,
    session: Optional[Session] = None
) -> Session:
    """Creates a context for a scoped database session. If the session is supplied, that session is used. Otherwise, a new scoped session is created."""

    logger = logging.getLogger(__name__)
    factory = DatabaseManager.get_scoped_factory(db, env)
    is_owner = session is None
    db_session = session if not is_owner else factory()

    try:
        yield db_session

        if is_owner:
            db_session.commit()
    except Exception as error:
        if is_owner:
            db_session.rollback()

        raise
    finally:
        if is_owner:
            factory.remove()

    return


T = TypeVar('T', bound=Callable)


def uses_db_session(func, T) -> T:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'db_session' in kwargs:
            return func(*args, **kwargs)

        with db_context() as db_session:
            kwargs['db_session'] = db_session

            return func(*args, **kwargs)

    return wrapper
