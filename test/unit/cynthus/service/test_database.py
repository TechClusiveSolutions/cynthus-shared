from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.engine import make_url

from cynthus.service import database as database_module
from cynthus.service.database import Database
from cynthus.service.database_target import DatabaseTarget


def test_nothing_connects_until_a_session_is_requested():
    with patch.object(database_module, 'create_async_engine') as engine:
        Database(url='postgresql+psycopg://u:p@db/x')

    engine.assert_not_called()


def test_the_engine_is_created_once_and_reused():
    with patch.object(database_module, 'create_async_engine') as engine, \
            patch.object(database_module, 'async_sessionmaker') as sessions:
        database = Database(url='postgresql+psycopg://u:p@db/x')
        first, second = database.session(), database.session()

    engine.assert_called_once()
    assert engine.call_args.args[0] == 'postgresql+psycopg://u:p@db/x'
    assert first is second is sessions.return_value.return_value


def test_the_url_comes_from_the_environment_by_default(monkeypatch):
    monkeypatch.setenv('DB_NAME', 'core')

    with patch.object(database_module, 'create_async_engine') as engine, \
            patch.object(database_module, 'async_sessionmaker'):
        Database().session()

    assert engine.call_args.args[0].database == 'core'


@pytest.mark.asyncio
async def test_dispose_closes_the_engine_and_allows_a_fresh_one():
    engine = MagicMock(dispose=AsyncMock())

    with patch.object(database_module, 'create_async_engine', return_value=engine) as create, \
            patch.object(database_module, 'async_sessionmaker'):
        database = Database(url='postgresql+psycopg://u:p@db/x')
        database.session()
        await database.dispose()
        database.session()

    engine.dispose.assert_awaited_once()
    assert create.call_count == 2


@pytest.mark.asyncio
async def test_dispose_without_a_session_does_nothing():
    await Database(url='postgresql+psycopg://u:p@db/x').dispose()


def _environment(monkeypatch):
    for key, value in {
        'DB_NAME': 'cynthus_partner', 'DB_USERNAME': 'partner_admin', 'DB_PASSWORD': 'p',
        'TEST_DB_NAME': 'cynthus_partner', 'TEST_DB_USERNAME': 'partner_test', 'TEST_DB_PASSWORD': 't',
    }.items():
        monkeypatch.setenv(key, value)


def test_engine_without_a_target_is_the_default_engine():
    with patch.object(database_module, 'create_async_engine') as engine, \
            patch.object(database_module, 'async_sessionmaker'):
        database = Database(url='postgresql+psycopg://u:p@db/x')

        assert database.engine() is engine.return_value
        assert database.engine() is engine.return_value

    engine.assert_called_once()


def test_engine_for_a_target_sets_the_schema_and_is_cached(monkeypatch):
    _environment(monkeypatch)
    target = DatabaseTarget.resolve('testing', 'partner')

    with patch.object(database_module, 'create_async_engine') as engine, \
            patch.object(database_module, 'async_sessionmaker'):
        database = Database()

        assert database.engine(target) is database.engine(target) is engine.return_value

    engine.assert_called_once()
    assert engine.call_args.args[0].username == 'partner_test'
    assert engine.call_args.kwargs['connect_args'] == {'options': '-csearch_path=test_partner'}


def test_each_target_gets_its_own_engine(monkeypatch):
    _environment(monkeypatch)

    with patch.object(database_module, 'create_async_engine', side_effect=[MagicMock(), MagicMock()]) as engine, \
            patch.object(database_module, 'async_sessionmaker'):
        database = Database()
        production = database.engine(DatabaseTarget.resolve('production', 'partner'))
        testing = database.engine(DatabaseTarget.resolve('testing', 'partner'))

    assert production is not testing
    assert engine.call_count == 2


def test_a_target_without_a_schema_sets_no_search_path():
    target = DatabaseTarget(make_url('postgresql+psycopg://u:p@db/x'))

    with patch.object(database_module, 'create_async_engine') as engine, \
            patch.object(database_module, 'async_sessionmaker'):
        Database().engine(target)

    assert 'connect_args' not in engine.call_args.kwargs


def test_get_session_builds_a_session_for_the_environment_and_service(monkeypatch):
    _environment(monkeypatch)

    with patch.object(database_module, 'create_async_engine') as engine, \
            patch.object(database_module, 'async_sessionmaker') as sessions:
        session = Database().get_session('production', 'partner')

    assert session is sessions.return_value.return_value
    assert engine.call_args.args[0].username == 'partner_admin'
    assert engine.call_args.kwargs['connect_args'] == {'options': '-csearch_path=partner'}


def test_get_session_refuses_an_unknown_environment():
    with pytest.raises(ValueError, match='Unknown environment'):
        Database().get_session('staging', 'partner')


@pytest.mark.asyncio
async def test_dispose_closes_every_engine(monkeypatch):
    _environment(monkeypatch)
    engines = [MagicMock(dispose=AsyncMock()), MagicMock(dispose=AsyncMock())]

    with patch.object(database_module, 'create_async_engine', side_effect=engines), \
            patch.object(database_module, 'async_sessionmaker'):
        database = Database(url='postgresql+psycopg://u:p@db/x')
        database.engine()
        database.engine(DatabaseTarget.resolve('production', 'partner'))
        await database.dispose()

    for engine in engines:
        engine.dispose.assert_awaited_once()
