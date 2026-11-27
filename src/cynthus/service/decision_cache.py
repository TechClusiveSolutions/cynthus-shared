"""Short-term cache of event request decisions for the Cynthus project"""

from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from uuid import UUID

from pydantic import ValidationError

from cynthus.core import logging
from cynthus.core.event import EventRequestDecisionData, EventRequestResponse
from cynthus.core.redis import RedisClient

LOGGER = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DecisionCache:
    """Keeps the latest decision of an event request for a while (ADR-013); decisions are not stored per service.

    The cached value is the decision as ``EventRequestDecisionData`` (JSON), under the key ``decision:<event_request_id>``.
    It lives for ``ttl``; a decision with open conditions lives until the latest of them expires when that is later, so a
    pending approval can be found until it expires. A cache failure is logged and never raised: the decision stands.
    """

    def __init__(
        self,
        redis: RedisClient,
        ttl: timedelta = timedelta(hours=24),
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self.redis = redis
        self.ttl = ttl
        self.clock = clock

    @staticmethod
    def key(event_request_id: UUID) -> str:
        return f'decision:{event_request_id}'

    async def put(self, response: EventRequestResponse) -> None:
        """Caches the latest decision of ``response``; a response without a decision is not cached."""

        decision = response.decision

        if decision is None:
            return

        try:
            data = EventRequestDecisionData.from_decision(response.request, decision)

            await self.redis.set(
                self.key(data.event_request_id), data.model_dump(mode='json'), self._expiry(response)
            )
        except Exception:
            LOGGER.getChild('put').exception('Could not cache the decision of event request %s', response.request.id_)

    async def get(self, event_request_id: UUID) -> EventRequestDecisionData | None:
        """The cached decision of the request, or None when there is none, it is corrupt or the cache failed."""

        try:
            value = await self.redis.get(self.key(event_request_id))

            if value is None:
                return None

            return EventRequestDecisionData.model_validate(value)
        except (ValidationError, TypeError):
            LOGGER.getChild('get').exception('The cached decision of event request %s is corrupt', event_request_id)
        except Exception:
            LOGGER.getChild('get').exception('Could not read the decision of event request %s', event_request_id)

        return None

    def _expiry(self, response: EventRequestResponse) -> int:
        """Seconds to keep the decision: ``ttl``, or until the latest open condition expires when later."""

        seconds = self.ttl.total_seconds()
        now = self.clock()

        for condition in response.decision.conditions:
            if condition.is_open and condition.expires_at is not None:
                expires_at = condition.expires_at

                # A time without a zone is read as UTC, like the rest of the platform
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)

                seconds = max(seconds, (expires_at - now).total_seconds())

        return max(1, round(seconds))
