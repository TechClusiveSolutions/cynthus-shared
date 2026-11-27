"""Partner Service List Responded Event class for the Cynthus project"""

from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel

from .event_action import EventAction
from .partner_event import PartnerEvent
from .partner_service_list_requested_event import PartnerServiceListRequestedEvent
from .partner_service_list_responded_data import PartnerServiceListRespondedData


class PartnerServiceListRespondedEvent(PartnerEvent):
    """Represents the answer to a request for the list of services offered by partners"""

    data_model: ClassVar[type[BaseModel] | None] = PartnerServiceListRespondedData

    @classmethod
    def answering(
        cls,
        request: PartnerServiceListRequestedEvent,
        *,
        status: int,
        items: Sequence[tuple[UUID, str]] | None = None,
        error: str | None = None,
    ) -> PartnerServiceListRespondedEvent:
        """
            A new event that answers ``request``

            Copies the correlation id, the ids and the service id of the request, and gets its own ``id_`` and
            ``occurred_on``. ``items`` are pairs of service id and name; without them ``result`` is ``None``.
        """

        result = None if items is None else [{'id': item_id, 'name': name} for item_id, name in items]

        # The data is the complete data model in JSON form (ids as text, defaults filled in), exactly what
        # SignalEventReader gives back for the signal of this event, so both events carry equal data
        data = PartnerServiceListRespondedData(status=status, result=result, error=error).model_dump(mode='json')

        return cls(
            correlation_id=request.correlation_id,
            tenant_id=request.tenant_id,
            workspace_id=request.workspace_id,
            actor_id=request.actor_id,
            service_id=request.service_id,
            action=EventAction.RETRIEVED,
            data=data,
        )
