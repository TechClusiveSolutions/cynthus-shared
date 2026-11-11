"""Service core model class for the Cynthus project"""

from pydantic import BaseModel, Field
from uuid import UUID

from .service_domain import ServiceDomain

from ...messaging.common.signal import SignalMessage

# from ...messaging.signal import GenericSignalMessageGenerator, SignalMessage


class Service(BaseModel):
    """Represents a Cynthus service application"""

    id_: UUID
    name: str
    domain: ServiceDomain
    # generator: SignalMessageGenerator = Field(default_factory=lambda: GenericSignalMessageGenerator())


    def publish_message(self) -> SignalMessage:
        pass
