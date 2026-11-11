"""Signal Message Base class for the Cynthus project"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import Field, model_validator

from .lifecycle_action import LifecycleAction
from .part import SignalPart


class SignalMessageBase(SignalPart):
    """Base structural model enforcing multi-tenant isolation contexts."""

    event_id: UUID = Field(
        default_factory=uuid4
    )

    event_type: str = Field(..., description="Dot-notated routing string.")
    lifecycle_action: LifecycleAction
    correlation_id: UUID = Field(..., description="CrossServiceCorrelationGuid.")
    organization_id: UUID = Field(..., description="Deprecated alias of tenant_id (ADR-010); the same value.")
    tenant_id: UUID = Field(..., description="The tenant boundary identifier; the same value as organization_id.")
    workspace_id: UUID = Field(..., description="Functional Isolation partition tracking key.")
    actor_id: UUID = Field(..., description="The unique system or user identity executing the shift.")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode='before')
    @classmethod
    def _tenant_is_organization(cls, data):
        """ADR-010: ``tenant_id`` replaces ``organization_id`` additively. Either may be given and both are set; they are
        one value, so two different ones are refused. A signal from a publisher that knows only ``organization_id`` reads
        as before."""

        if not isinstance(data, dict):
            return data

        organization, tenant = data.get('organization_id'), data.get('tenant_id')

        if organization is not None and tenant is not None and str(organization) != str(tenant):
            raise ValueError('tenant_id and organization_id are one value; they differ')

        value = tenant if tenant is not None else organization

        return data if value is None else {**data, 'organization_id': value, 'tenant_id': value}
