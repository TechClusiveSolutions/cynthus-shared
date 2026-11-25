"""Signal Event class for the Cynthus project"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, ClassVar, Self, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, model_validator

from .event_action import EventAction
from .event_type_name import event_type_name

ModelT = TypeVar('ModelT', bound=BaseModel)


class SignalEvent(BaseModel):
    """Represents an action asked for by a received signal, known by ids only (no database read is needed to build it)"""

    model_config = ConfigDict(frozen=True)

    id_: UUID = Field(default_factory=uuid4)
    correlation_id: UUID = Field(default_factory=uuid4)
    occurred_on: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tenant_id: UUID
    workspace_id: UUID
    actor_id: UUID
    service_id: UUID | None = Field(default=None, description='The service that recorded the event')
    action: EventAction
    data: dict[str, Any]

    data_model: ClassVar[type[BaseModel] | None] = None
    actions: ClassVar[frozenset[EventAction] | None] = None

    _parsed_data: BaseModel | None = PrivateAttr(default=None)

    @model_validator(mode='after')
    def _validate_action(self) -> SignalEvent:
        """Check ``action`` against ``actions`` when the event class declares them"""

        if self.actions is not None and self.action not in self.actions:
            allowed = ', '.join(sorted(action.value for action in self.actions))

            raise ValueError(f'{type(self).__name__} does not allow the action {self.action.value!r} (allowed: {allowed})')

        return self

    @model_validator(mode='after')
    def _validate_data(self) -> SignalEvent:
        """Check ``data`` against ``data_model`` when the event class declares one"""

        if self.data_model is not None:
            self._parsed_data = self.data_model.model_validate(self.data)

        return self

    def parsed_data(self, model: type[ModelT]) -> ModelT:
        """
            ``data`` as ``model``

            Returns the model parsed when the event was created if it is an instance of ``model``, so typed data is
            parsed once; otherwise validates ``data`` against ``model``. Do not change ``data`` after creation.
        """

        if isinstance(self._parsed_data, model):
            return self._parsed_data

        return model.model_validate(self.data)

    def __hash__(self) -> int:
        """The hash of ``id_`` (equal events have equal ids); a frozen model cannot hash its ``data`` dict"""

        return hash(self.id_)

    def model_copy(self, *, update: dict[str, Any] | None = None, deep: bool = False) -> Self:
        """
            A copy of the event, validated again

            Builds the copy from the field values plus ``update`` (deep copied when ``deep`` is set) and validates it,
            so the action check and the ``data_model`` check run and the parsed data is rebuilt. The copy keeps ``id_``
            unless ``update`` changes it. Without ``deep`` the copy shares nested values (such as lists inside
            ``data``) with the original. ``ValueError`` when ``update`` names something that is not a field.
        """

        values = {name: getattr(self, name) for name in type(self).model_fields}
        unknown = sorted(set(update or {}) - set(values))

        if unknown:
            raise ValueError(f'{type(self).__name__} has no field {", ".join(unknown)}')

        values.update(update or {})

        if deep:
            values = deepcopy(values)

        return type(self).model_validate(values)

    @property
    def event_type(self) -> str:
        """The snake_case class name without a trailing ``Event`` (``PartnerServiceListRequestedEvent`` is
        ``partner_service_list_requested``; ``SignalEvent`` is ``signal``)"""

        return event_type_name(type(self).__name__)
