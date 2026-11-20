"""Inventory Shelf Signal Generator class for the Cynthus project"""

from __future__ import annotations

from typing import ClassVar

from .....core.event import Event, InventoryShelfCreatedData, InventoryShelfDeletedData, InventoryShelfUpdatedData
from ....common.signal.lifecycle_action import LifecycleAction
from ....common.signal.public_inventory_shelf_created import PublicInventoryShelfCreatedSignal
from ....common.signal.public_inventory_shelf_deleted import PublicInventoryShelfDeletedSignal
from ....common.signal.public_inventory_shelf_updated import PublicInventoryShelfUpdatedSignal
from ....generator import SignalContract, SignalGenerator
from ..message import InventoryShelfCreatedMessage, InventoryShelfDeletedMessage, InventoryShelfUpdatedMessage
from ..payload import InventoryShelfCreatedPayload, InventoryShelfDeletedPayload, InventoryShelfUpdatedPayload


class InventoryShelfSignalGenerator(SignalGenerator):
    """Generates the created, updated and deleted signals of an inventory shelf"""

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
        SignalContract(
            features=('FT-IM-001',),
            event='InventoryShelfUpdatedEvent',
            signal=PublicInventoryShelfUpdatedSignal,
            message=InventoryShelfUpdatedMessage,
            payload=InventoryShelfUpdatedPayload,
            lifecycle_action=LifecycleAction.UPDATED,
            method='updated',
            sources={
                'shelf_id': 'data.shelf_id',
                'location_id': 'data.location_id',
                'name': 'data.name',
                'position': 'data.position',
            },
        ),
        SignalContract(
            features=('FT-IM-001',),
            event='InventoryShelfDeletedEvent',
            signal=PublicInventoryShelfDeletedSignal,
            message=InventoryShelfDeletedMessage,
            payload=InventoryShelfDeletedPayload,
            lifecycle_action=LifecycleAction.DELETED,
            method='deleted',
            sources={
                'shelf_id': 'data.shelf_id',
                'location_id': 'data.location_id',
            },
        ),
    )

    def created(self, event: Event) -> InventoryShelfCreatedMessage:
        """The message for a created shelf, from the data of the event"""

        contract = self.contract('created')
        data = event.parsed_data(InventoryShelfCreatedData)
        payload = InventoryShelfCreatedPayload(
            shelf_id=data.shelf_id,
            location_id=data.location_id,
            name=data.name,
            position=data.position,
            observed_at=event.occurred_on,
        )

        return contract.message(**self.envelope(event, contract), payload=payload)

    def updated(self, event: Event) -> InventoryShelfUpdatedMessage:
        """The message for an updated shelf, from the data of the event"""

        contract = self.contract('updated')
        data = event.parsed_data(InventoryShelfUpdatedData)
        payload = InventoryShelfUpdatedPayload(
            shelf_id=data.shelf_id,
            location_id=data.location_id,
            name=data.name,
            position=data.position,
            observed_at=event.occurred_on,
        )

        return contract.message(**self.envelope(event, contract), payload=payload)

    def deleted(self, event: Event) -> InventoryShelfDeletedMessage:
        """The message for a deleted shelf, from the data of the event"""

        contract = self.contract('deleted')
        data = event.parsed_data(InventoryShelfDeletedData)
        payload = InventoryShelfDeletedPayload(
            shelf_id=data.shelf_id, location_id=data.location_id, observed_at=event.occurred_on
        )

        return contract.message(**self.envelope(event, contract), payload=payload)
