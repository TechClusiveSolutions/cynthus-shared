"""Partner Signal Generator class for the Cynthus project"""

from __future__ import annotations

from typing import ClassVar

from .....core.event import (
    PartnerServiceListRequestedData,
    PartnerServiceListRequestedEvent,
    PartnerServiceListRespondedData,
    PartnerServiceListRespondedEvent,
)
from ....common.signal.lifecycle_action import LifecycleAction
from ....common.signal.public_partner_service_list_requested import PublicPartnerServiceListRequestedSignal
from ....common.signal.public_partner_service_list_responded import PublicPartnerServiceListRespondedSignal
from ....generator import SignalContract, SignalGenerator
from ..message import PartnerServiceListRequestedMessage, PartnerServiceListRespondedMessage
from ..payload import (
    PartnerServiceListFilters,
    PartnerServiceListItem,
    PartnerServiceListRequestedPayload,
    PartnerServiceListRespondedPayload,
)


class PartnerSignalGenerator(SignalGenerator):
    """Generates the requested and responded signals of the partner service list"""

    contracts: ClassVar[tuple[SignalContract, ...]] = (
        SignalContract(
            features=('FT-SR-006',),
            event='PartnerServiceListRequestedEvent',
            signal=PublicPartnerServiceListRequestedSignal,
            message=PartnerServiceListRequestedMessage,
            payload=PartnerServiceListRequestedPayload,
            lifecycle_action=LifecycleAction.UPDATED,
            method='requested',
            sources={'schema_version': 'data.schema_version', 'filters': 'data.filters'},
        ),
        SignalContract(
            features=('FT-SR-006',),
            event='PartnerServiceListRespondedEvent',
            signal=PublicPartnerServiceListRespondedSignal,
            message=PartnerServiceListRespondedMessage,
            payload=PartnerServiceListRespondedPayload,
            lifecycle_action=LifecycleAction.UPDATED,
            method='responded',
            sources={
                'schema_version': 'data.schema_version',
                'status': 'data.status',
                'result': 'data.result',
                'error': 'data.error',
            },
        ),
    )

    def requested(self, event: PartnerServiceListRequestedEvent) -> PartnerServiceListRequestedMessage:
        """The message for a service list request, from the data of the event"""

        contract = self.contract('requested')
        data = event.parsed_data(PartnerServiceListRequestedData)
        payload = PartnerServiceListRequestedPayload(
            schema_version=data.schema_version,
            filters=PartnerServiceListFilters(name=data.filters.name),
            observed_at=event.occurred_on,
        )

        return contract.message(**self.envelope(event, contract), payload=payload)

    def responded(self, event: PartnerServiceListRespondedEvent) -> PartnerServiceListRespondedMessage:
        """The message for the answer to a service list request, from the data of the event"""

        contract = self.contract('responded')
        data = event.parsed_data(PartnerServiceListRespondedData)
        result = None if data.result is None else [PartnerServiceListItem(id=i.id, name=i.name) for i in data.result]
        payload = PartnerServiceListRespondedPayload(
            schema_version=data.schema_version,
            status=data.status,
            result=result,
            error=data.error,
            observed_at=event.occurred_on,
        )

        return contract.message(**self.envelope(event, contract), payload=payload)
