"""Scheduler Signal Subscription class for the Cynthus project"""

from .public_subscription import PublicSubscription


class SchedulerSignalSubscription(PublicSubscription):
    """Represents the Scheduler's subscription to `cynthus-events-topic`."""

    name: str = 'cynthus-sub-scheduler'
