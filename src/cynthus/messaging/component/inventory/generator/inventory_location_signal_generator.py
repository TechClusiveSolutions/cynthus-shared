"""Inventory Location Signal Generator class for the Cynthus project"""

from __future__ import annotations

from typing import ClassVar

from .....core.event import Event, InventoryLocationCreatedData
from ....common.signal.lifecycle_action import LifecycleAction
from ....common.signal.public_inventory_location_created import PublicInventoryLocationCreatedSignal
from ....generator import SignalContract, SignalGenerator
from ..message import InventoryLocationCreatedMessage
from ..payload import InventoryLocationCreatedPayload


class InventoryLocationSignalGenerator(SignalGenerator):
    """Generates the signals of an inventory location: ``public.inventory.location.created``"""

    contracts: ClassVar[tuple[SignalContract, ...]] = (
        SignalContract(
            features=('FT-IM-001',),
            event='InventoryLocationCreatedEvent',
            signal=PublicInventoryLocationCreatedSignal,
            message=InventoryLocationCreatedMessage,
            payload=InventoryLocationCreatedPayload,
            lifecycle_action=LifecycleAction.CREATED,
            method='created',
            sources={
                'location_id': 'data.location_id',
                'name': 'data.name',
                'type': 'data.type',
            },
        ),
    )

    def created(self, event: Event) -> InventoryLocationCreatedMessage:
        """The message for a created location, from the data of the event"""

        contract = self.contract('created')
        data = InventoryLocationCreatedData.model_validate(event.data)
        payload = InventoryLocationCreatedPayload(
            location_id=data.location_id, name=data.name, type=data.type, observed_at=event.occurred_on
        )

        return contract.message(**self.envelope(event, contract), payload=payload)
