"""Inventory Location Signal Generator class for the Cynthus project"""

from __future__ import annotations

from typing import ClassVar

from .....core.event import (
    Event,
    InventoryLocationCreatedData,
    InventoryLocationDeletedData,
    InventoryLocationUpdatedData,
)
from ....common.signal.lifecycle_action import LifecycleAction
from ....common.signal.public_inventory_location_created import PublicInventoryLocationCreatedSignal
from ....common.signal.public_inventory_location_deleted import PublicInventoryLocationDeletedSignal
from ....common.signal.public_inventory_location_updated import PublicInventoryLocationUpdatedSignal
from ....generator import SignalContract, SignalGenerator
from ..message import InventoryLocationCreatedMessage, InventoryLocationDeletedMessage, InventoryLocationUpdatedMessage
from ..payload import InventoryLocationCreatedPayload, InventoryLocationDeletedPayload, InventoryLocationUpdatedPayload


class InventoryLocationSignalGenerator(SignalGenerator):
    """Generates the created, updated and deleted signals of an inventory location"""

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
        SignalContract(
            features=('FT-IM-001',),
            event='InventoryLocationUpdatedEvent',
            signal=PublicInventoryLocationUpdatedSignal,
            message=InventoryLocationUpdatedMessage,
            payload=InventoryLocationUpdatedPayload,
            lifecycle_action=LifecycleAction.UPDATED,
            method='updated',
            sources={
                'location_id': 'data.location_id',
                'name': 'data.name',
                'type': 'data.type',
                'archived': 'data.archived',
            },
        ),
        SignalContract(
            features=('FT-IM-001',),
            event='InventoryLocationDeletedEvent',
            signal=PublicInventoryLocationDeletedSignal,
            message=InventoryLocationDeletedMessage,
            payload=InventoryLocationDeletedPayload,
            lifecycle_action=LifecycleAction.DELETED,
            method='deleted',
            sources={
                'location_id': 'data.location_id',
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

    def updated(self, event: Event) -> InventoryLocationUpdatedMessage:
        """The message for an updated location, from the data of the event"""

        contract = self.contract('updated')
        data = InventoryLocationUpdatedData.model_validate(event.data)
        payload = InventoryLocationUpdatedPayload(
            location_id=data.location_id,
            name=data.name,
            type=data.type,
            archived=data.archived,
            observed_at=event.occurred_on,
        )

        return contract.message(**self.envelope(event, contract), payload=payload)

    def deleted(self, event: Event) -> InventoryLocationDeletedMessage:
        """The message for a deleted location, from the data of the event"""

        contract = self.contract('deleted')
        data = InventoryLocationDeletedData.model_validate(event.data)
        payload = InventoryLocationDeletedPayload(
            location_id=data.location_id, observed_at=event.occurred_on
        )

        return contract.message(**self.envelope(event, contract), payload=payload)
