"""Tests for cynthus.service.decision_cache (DecisionCache)."""

import json
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from cynthus.core.event import EventRequestDecisionData, EventRequestResponse
from cynthus.core.test.factory.event import EventRequestResponseFactory
from cynthus.service import DecisionCache

DAY = 24 * 3600
TOLERANCE = 2  # seconds; conditions are built from the real clock, the cache clock is the real one too


class FakeRedis:
    """Records what is stored and with which expiry; can be told to fail."""

    def __init__(self, error: Exception | None = None):
        self.values = {}
        self.expiries = {}
        self.error = error

    async def set(self, key, value, expiry=3600):
        if self.error:
            raise self.error

        self.values[key] = value
        self.expiries[key] = expiry

    async def get(self, key, default=None):
        if self.error:
            raise self.error

        return self.values.get(key, default)


def an_approved_response() -> EventRequestResponse:
    response = EventRequestResponseFactory()
    response.approve('permitted')

    return response


def a_conditional_response(*expiries) -> EventRequestResponse:
    response = EventRequestResponseFactory()
    decision = response.conditionally_approve('approval_required', ['approval_granted'] * max(len(expiries), 1))

    for condition, expires_at in zip(decision.conditions, expiries):
        condition.expires_at = expires_at

    return response


def in_days(days: float) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=days)


def key_of(response: EventRequestResponse) -> str:
    return f'decision:{response.request.id_}'


def seconds_of(redis: FakeRedis, response: EventRequestResponse) -> float:
    expiry = redis.expiries[key_of(response)]

    return expiry.total_seconds() if isinstance(expiry, timedelta) else expiry


def expected_data(response: EventRequestResponse) -> EventRequestDecisionData:
    decision = response.decision
    requested = response.request.event

    return EventRequestDecisionData(
        event_request_id=response.request.id_,
        in_reply_to=response.request.in_reply_to,
        requested_event_type=requested.event_type,
        requested_action=requested.action.value,
        requestor_id=response.request.requestor_id,
        answer=decision.answer.value,
        answer_reason=decision.answer_reason,
        conditions=[
            {'condition': c.condition, 'status': c.status.value, 'expires_at': c.expires_at} for c in decision.conditions
        ],
        determined_by=decision.determined_by,
        determined_on=decision.determined_on,
    )


@pytest.mark.asyncio
async def test_put_then_get_returns_equal_data_for_an_approval():
    response = an_approved_response()
    cache = DecisionCache(FakeRedis())

    await cache.put(response)
    cached = await cache.get(response.request.id_)

    assert isinstance(cached, EventRequestDecisionData)
    assert cached == expected_data(response)


@pytest.mark.asyncio
async def test_put_then_get_returns_equal_data_for_a_denial():
    response = EventRequestResponseFactory()
    response.deny('forbidden')
    cache = DecisionCache(FakeRedis())

    await cache.put(response)

    assert await cache.get(response.request.id_) == expected_data(response)


@pytest.mark.asyncio
async def test_put_then_get_returns_equal_data_for_a_conditional_decision_with_conditions():
    response = a_conditional_response(in_days(5))
    cache = DecisionCache(FakeRedis())

    await cache.put(response)
    cached = await cache.get(response.request.id_)

    assert cached == expected_data(response)
    assert len(cached.conditions) == 1


@pytest.mark.asyncio
async def test_the_latest_decision_is_the_one_cached():
    response = a_conditional_response(in_days(5))
    response.approve('approval_granted')
    cache = DecisionCache(FakeRedis())

    await cache.put(response)

    cached = await cache.get(response.request.id_)

    assert cached.answer == 'approved'
    assert cached.conditions == []


@pytest.mark.asyncio
async def test_the_cached_value_is_json_not_the_full_response():
    response = an_approved_response()
    redis = FakeRedis()

    await DecisionCache(redis).put(response)

    stored = redis.values[key_of(response)]
    stored = json.loads(stored) if isinstance(stored, (str, bytes)) else stored

    assert stored['event_request_id'] == str(response.request.id_)
    assert 'decisions' not in stored and 'request' not in stored
    json.dumps(stored)


@pytest.mark.asyncio
async def test_an_unknown_id_returns_none():
    cache = DecisionCache(FakeRedis())

    assert await cache.get(UUID(int=1)) is None


@pytest.mark.asyncio
async def test_the_key_is_decision_and_the_request_id():
    response = an_approved_response()
    redis = FakeRedis()

    await DecisionCache(redis).put(response)

    assert list(redis.values) == [f'decision:{response.request.id_}']


@pytest.mark.asyncio
@pytest.mark.parametrize('answer', ['approve', 'deny'])
async def test_approved_and_denied_decisions_are_cached_for_24_hours(answer):
    response = EventRequestResponseFactory()
    getattr(response, answer)('reason')
    redis = FakeRedis()

    await DecisionCache(redis).put(response)

    assert seconds_of(redis, response) == DAY


@pytest.mark.asyncio
async def test_a_given_ttl_replaces_the_default():
    response = an_approved_response()
    redis = FakeRedis()

    await DecisionCache(redis, ttl=timedelta(hours=2)).put(response)

    assert seconds_of(redis, response) == 2 * 3600


@pytest.mark.asyncio
async def test_a_conditional_decision_expiring_in_5_days_is_cached_for_5_days():
    response = a_conditional_response(in_days(5))
    redis = FakeRedis()

    await DecisionCache(redis).put(response)

    assert seconds_of(redis, response) == pytest.approx(5 * DAY, abs=TOLERANCE)


@pytest.mark.asyncio
async def test_a_conditional_denial_is_cached_until_its_condition_expires():
    response = EventRequestResponseFactory()
    decision = response.conditionally_deny('approval_required', ['approval_granted'])
    decision.conditions[0].expires_at = in_days(3)
    redis = FakeRedis()

    await DecisionCache(redis).put(response)

    assert seconds_of(redis, response) == pytest.approx(3 * DAY, abs=TOLERANCE)


@pytest.mark.asyncio
async def test_the_latest_of_several_condition_expiries_decides():
    response = a_conditional_response(in_days(2), in_days(7), in_days(4))
    redis = FakeRedis()

    await DecisionCache(redis).put(response)

    assert seconds_of(redis, response) == pytest.approx(7 * DAY, abs=TOLERANCE)


@pytest.mark.asyncio
async def test_a_conditional_decision_expiring_within_24_hours_is_still_cached_for_24_hours():
    response = a_conditional_response(datetime.now(timezone.utc) + timedelta(hours=3))
    redis = FakeRedis()

    await DecisionCache(redis).put(response)

    assert seconds_of(redis, response) == DAY


@pytest.mark.asyncio
async def test_a_condition_that_expired_in_the_past_gives_the_default_ttl():
    response = a_conditional_response(in_days(-2))
    redis = FakeRedis()

    await DecisionCache(redis).put(response)

    assert seconds_of(redis, response) == DAY


@pytest.mark.asyncio
async def test_a_conditional_decision_without_expiry_gets_the_default_ttl():
    response = a_conditional_response(None)
    redis = FakeRedis()

    await DecisionCache(redis).put(response)

    assert seconds_of(redis, response) == DAY


@pytest.mark.asyncio
async def test_a_conditional_decision_without_conditions_gets_the_default_ttl():
    response = EventRequestResponseFactory()
    response.conditionally_approve('approval_required', [])
    redis = FakeRedis()

    await DecisionCache(redis).put(response)

    assert seconds_of(redis, response) == DAY


@pytest.mark.asyncio
async def test_a_longer_default_ttl_is_not_shortened_by_an_earlier_condition_expiry():
    response = a_conditional_response(in_days(2))
    redis = FakeRedis()

    await DecisionCache(redis, ttl=timedelta(days=10)).put(response)

    assert seconds_of(redis, response) == 10 * DAY


@pytest.mark.asyncio
async def test_two_requests_do_not_collide():
    first = an_approved_response()
    second = EventRequestResponseFactory()
    second.deny('forbidden')
    cache = DecisionCache(FakeRedis())

    await cache.put(first)
    await cache.put(second)

    assert await cache.get(first.request.id_) == expected_data(first)
    assert await cache.get(second.request.id_) == expected_data(second)
    assert (await cache.get(first.request.id_)).answer == 'approved'
    assert (await cache.get(second.request.id_)).answer == 'denied'


@pytest.mark.asyncio
async def test_a_put_again_for_the_same_request_replaces_the_decision():
    response = a_conditional_response(in_days(5))
    cache = DecisionCache(FakeRedis())

    await cache.put(response)
    response.deny('expired')
    await cache.put(response)

    assert (await cache.get(response.request.id_)).answer == 'denied'


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'corrupt', ['not json {', '{"event_request_id": "nope"}', '[]', '42', '{}', {'unexpected': 1}, ['x'], 7]
)
async def test_a_corrupt_cached_value_returns_none_and_logs(corrupt, caplog):
    request_id = UUID(int=7)
    redis = FakeRedis()
    redis.values[f'decision:{request_id}'] = corrupt

    with caplog.at_level(logging.DEBUG):
        assert await DecisionCache(redis).get(request_id) is None

    assert any(record.levelno >= logging.WARNING for record in caplog.records)


@pytest.mark.asyncio
async def test_a_value_with_an_unknown_extra_field_is_corrupt(caplog):
    response = an_approved_response()
    redis = FakeRedis()
    cache = DecisionCache(redis)

    await cache.put(response)
    stored = redis.values[key_of(response)]
    as_text = isinstance(stored, str)
    stored = json.loads(stored) if as_text else dict(stored)
    stored['extra'] = 1
    redis.values[key_of(response)] = json.dumps(stored) if as_text else stored

    with caplog.at_level(logging.DEBUG):
        assert await cache.get(response.request.id_) is None

    assert caplog.records


@pytest.mark.asyncio
@pytest.mark.parametrize('error', [ConnectionError('down'), TimeoutError('slow'), RuntimeError('boom')])
async def test_a_redis_error_in_put_is_logged_and_not_raised(error, caplog):
    response = an_approved_response()
    redis = FakeRedis(error)

    with caplog.at_level(logging.WARNING):
        result = await DecisionCache(redis).put(response)

    assert result is None
    assert redis.values == {}
    assert any(record.levelno >= logging.WARNING for record in caplog.records)


@pytest.mark.asyncio
@pytest.mark.parametrize('error', [ConnectionError('down'), TimeoutError('slow'), RuntimeError('boom')])
async def test_a_redis_error_in_get_returns_none_and_logs(error, caplog):
    redis = FakeRedis(error)

    with caplog.at_level(logging.WARNING):
        result = await DecisionCache(redis).get(UUID(int=3))

    assert result is None
    assert any(record.levelno >= logging.WARNING for record in caplog.records)


@pytest.mark.asyncio
async def test_a_fixed_clock_gives_an_exact_ttl():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    response = a_conditional_response(now + timedelta(days=5))
    redis = FakeRedis()

    await DecisionCache(redis, clock=lambda: now).put(response)

    assert seconds_of(redis, response) == 5 * DAY


@pytest.mark.asyncio
async def test_a_response_without_a_decision_is_silently_not_cached():
    response = EventRequestResponseFactory()
    redis = FakeRedis()

    await DecisionCache(redis).put(response)

    assert redis.values == {}


def test_the_key_helper():
    assert DecisionCache.key(UUID(int=5)) == f'decision:{UUID(int=5)}'


@pytest.mark.asyncio
async def test_the_stored_value_is_a_json_dict():
    response = an_approved_response()
    redis = FakeRedis()

    await DecisionCache(redis).put(response)

    assert redis.values[key_of(response)] == expected_data(response).model_dump(mode='json')


@pytest.mark.asyncio
async def test_a_naive_expiry_is_read_as_utc():
    response = a_conditional_response(datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=5))
    redis = FakeRedis()

    await DecisionCache(redis).put(response)

    assert seconds_of(redis, response) == pytest.approx(5 * DAY, abs=TOLERANCE)


@pytest.mark.asyncio
@pytest.mark.parametrize('status', ['satisfied', 'failed', 'waived', 'expired'])
async def test_conditions_that_are_not_open_do_not_extend_the_ttl(status):
    from cynthus.core.event import DecisionConditionStatus

    response = a_conditional_response(in_days(2), in_days(9))
    response.decision.conditions[1].status = DecisionConditionStatus(status)
    redis = FakeRedis()

    await DecisionCache(redis).put(response)

    assert seconds_of(redis, response) == pytest.approx(2 * DAY, abs=TOLERANCE)


@pytest.mark.asyncio
async def test_the_expiry_is_an_int_and_a_round_trip_works_through_the_real_redis_client():
    from cynthus.core.redis import RedisClient

    class Raw:
        def __init__(self):
            self.store, self.ex = {}, {}

        async def get(self, key):
            return self.store.get(key)

        async def set(self, key, value, ex=None):
            self.store[key], self.ex[key] = value, ex

    raw = Raw()
    client = RedisClient.__new__(RedisClient)
    client.url, client.client = 'redis://fake', raw
    response = a_conditional_response(in_days(5))
    cache = DecisionCache(client)

    await cache.put(response)

    key = key_of(response)

    assert isinstance(raw.ex[key], int) and not isinstance(raw.ex[key], bool)
    assert isinstance(raw.store[key], str)
    assert await cache.get(response.request.id_) == expected_data(response)
