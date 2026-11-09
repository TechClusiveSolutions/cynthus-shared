"""Service outage flag for the Cynthus project"""

from cynthus.core import logging

LOGGER = logging.getLogger(__name__)

KEY = 'cynthus:outage'
TTL_SECONDS = 30


class ServiceOutage:
    """
        A shared "the service is out" flag in Redis, with an expiry, so it clears itself

        A service that finds the signal bus unreachable calls `report()`, and keeps calling it while the problem lasts.
        Nobody has to clear the flag: when the reports stop, it expires. The Session service reads it (`active()`) to
        tell the web and, later, the mobile app that the service is unavailable.

        Redis being unreachable is never turned into an outage here: the flag is a convenience on top of the services'
        own errors, so a failure to read or write it is logged and ignored.
    """

    ttl_seconds = TTL_SECONDS

    def __init__(self, redis) -> None:
        self._redis = redis

    async def report(self, reason: str = 'signal-bus') -> None:
        try:
            await self._redis.set(KEY, reason, expiry=self.ttl_seconds)
        except Exception:
            LOGGER.getChild('report').exception('Could not record the outage')

    async def active(self) -> bool:
        try:
            return await self._redis.exists(KEY)
        except Exception:
            LOGGER.getChild('active').exception('Could not read the outage flag')

            return False
