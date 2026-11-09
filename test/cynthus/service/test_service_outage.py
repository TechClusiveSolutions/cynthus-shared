"""Tests for cynthus.service.service_outage (ServiceOutage)."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from cynthus.service import ServiceOutage
from cynthus.service.service_outage import KEY, TTL_SECONDS


def a_redis():
    redis = MagicMock()
    redis.set = AsyncMock()
    redis.exists = AsyncMock(return_value=True)

    return redis


@pytest.mark.asyncio
async def test_a_report_sets_the_flag_with_an_expiry():
    redis = a_redis()

    await ServiceOutage(redis).report()

    redis.set.assert_awaited_once_with(KEY, 'signal-bus', expiry=TTL_SECONDS)


@pytest.mark.asyncio
async def test_the_flag_is_active_while_it_exists():
    redis = a_redis()

    assert await ServiceOutage(redis).active() is True

    redis.exists.return_value = False

    assert await ServiceOutage(redis).active() is False


@pytest.mark.asyncio
async def test_a_redis_that_cannot_be_reached_is_not_turned_into_an_outage(caplog):
    redis = a_redis()
    redis.set.side_effect = ConnectionError('down')
    redis.exists.side_effect = ConnectionError('down')
    outage = ServiceOutage(redis)

    await outage.report()

    assert await outage.active() is False
    assert 'Could not record the outage' in caplog.text and 'Could not read the outage flag' in caplog.text
