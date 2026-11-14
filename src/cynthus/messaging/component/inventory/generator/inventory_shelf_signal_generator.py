"""Inventory Shelf Signal Generator class for the Cynthus project"""

from __future__ import annotations

from typing import ClassVar

from .....core.event import Event, InventoryShelfCreatedData
from ....common.signal.lifecycle_action import LifecycleAction
from ....common.signal.public_inventory_shelf_created import PublicInventoryShelfCreatedSignal
from ....generator import SignalContract, SignalGenerator
from ..message import InventoryShelfCreatedMessage
from ..payload import InventoryShelfCreatedPayload


class InventoryShelfSignalGenerator(SignalGenerator):
    """Generates the signals of an inventory shelf: ``public.inventory.shelf.created``"""

    contracts: ClassVar[tuple[SignalContract, ...]] = (
        SignalContract(
            features=('FT-IM-001',),
            event='InventoryShelfCreatedEvent',
            signal=PublicInventoryShelfCreatedSignal,
            message=InventoryShelfCreatedMessage,
            payload=InventoryShelfCreatedPayload,
            lifecycle_action=LifecycleAction.CREATED,
            method='created',
            sources={
                'shelf_id': 'data.shelf_id',
                'location_id': 'data.location_id',
                'name': 'data.name',
                'position': 'data.position',
            },
        ),
    )

    def created(self, event: Event) -> InventoryShelfCreatedMessage:
        """The message for a created shelf, from the data of the event"""

        contract = self.contract('created')
        data = InventoryShelfCreatedData.model_validate(event.data)
        payload = InventoryShelfCreatedPayload(
            shelf_id=data.shelf_id,
            location_id=data.location_id,
            name=data.name,
            position=data.position,
            observed_at=event.occurred_on,
        )

        return contract.message(**self.envelope(event, contract), payload=payload)
