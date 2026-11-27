"""Decides an event request from the verified token claims (ADR-013)."""

from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from uuid import UUID

from cynthus.core.event import DecisionCondition, EventRequest, EventRequestAnswerReason, EventRequestResponse
from cynthus.security import TokenClaims


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DecisionPolicy:
    """The rules that answer an event request on behalf of a service, the same way for every service.

    The rules run in order and the first that applies decides:

    1. the claims lack the permission: denied, ``insufficient_privileges``;
    2. the resource belongs to the platform (no tenant): approved, ``access_permitted``;
    3. the resource is in the caller's tenant and the caller owns it: approved, ``permitted``;
    4. the resource is in the caller's tenant: approved, ``access_permitted``;
    5. the resource is in another tenant: approved conditionally, ``approval_required``, until an ``approval_granted``
       reply arrives or ``approval_expiry`` has passed.

    Only the clock is read, so a fixed clock gives equal answers.
    """

    def __init__(
        self,
        determined_by: UUID | None = None,
        approval_expiry: timedelta = timedelta(days=5),
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self.determined_by = determined_by
        self.approval_expiry = approval_expiry
        self.clock = clock

    def decide(
        self,
        request: EventRequest,
        claims: TokenClaims,
        *,
        permission: str,
        resource_tenant_id: UUID | None = None,
    ) -> EventRequestResponse:
        """Returns the response to ``request`` holding the one decision the rules give."""

        response = EventRequestResponse(request=request)
        by = self.determined_by

        if not claims.has_permission(permission):
            response.deny(EventRequestAnswerReason.INSUFFICIENT_PRIVILEGES, by)
        elif resource_tenant_id is None:
            response.approve(EventRequestAnswerReason.ACCESS_PERMITTED, by)
        elif resource_tenant_id == claims.tenant_id and claims.owner:
            response.approve(EventRequestAnswerReason.PERMITTED, by)
        elif resource_tenant_id == claims.tenant_id:
            response.approve(EventRequestAnswerReason.ACCESS_PERMITTED, by)
        else:
            response.conditionally_approve(
                EventRequestAnswerReason.APPROVAL_REQUIRED,
                [DecisionCondition(
                    condition=EventRequestAnswerReason.APPROVAL_GRANTED.value,
                    expires_at=self.clock() + self.approval_expiry,
                )],
                by,
            )

        return response
