"""Signal Topic base class for the Cynthus project"""

from pydantic import BaseModel


class SignalTopic(BaseModel):
    """Represents one Azure Service Bus topic."""

    name: str
