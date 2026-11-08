"""Published Signal class for the Cynthus project"""

from pydantic import BaseModel, ConfigDict

from ..common.signal.message_base import SignalMessageBase


class PublishedSignal(BaseModel):
    """A signal recorded by the in-memory bus: the topic it went to, the message itself and the access token it carried, if any."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    topic_name: str
    message: SignalMessageBase
    access_token: str | None = None
