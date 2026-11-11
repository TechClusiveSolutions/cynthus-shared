"""Service module for the Cynthus project"""

from dataclasses import dataclass, field


@dataclass
class ServiceModule:
    """
        One domain service hosted by a `ServiceApplication`

        A module is what a service gives `ServiceApplication` today: its routers, the subscription it listens on and the
        handler for it, the `SignalAccess` that records its access decisions, its database, and optional start-up and
        shutdown hooks. An application hosts one module (the usual case) or several (ADR-008), in one process and over
        one broker connection. A module with no subscription has no bus: it takes no part in the signal health.

        ``service`` is the identity of the service (``cynthus.core.service.Service``, ADR-009): its fixed id, name and
        domain. Give it and the module takes its name from it, and the health names the service by id. A module without
        one needs a ``name``.
    """

    name: str | None = None
    routers: list = field(default_factory=list)
    subscription: object = None
    handler: object = None
    signal_access: object = None
    database: object = None
    startup: object = None
    shutdown: object = None
    service: object = None

    def __post_init__(self) -> None:
        if self.service is not None:
            if self.name is None:
                self.name = self.service.name
            elif self.name != self.service.name:
                raise ValueError(f'the module name {self.name!r} is not the name of its service {self.service.name!r}')

        if not self.name:
            raise ValueError('a module needs a name or a service')

        if (self.subscription is None) != (self.handler is None):
            raise ValueError('a subscription and its handler go together: give both or neither')

        self.routers = list(self.routers)
