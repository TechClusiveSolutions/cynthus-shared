from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cynthus.service import database as database_module
from cynthus.service.database import Database


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
