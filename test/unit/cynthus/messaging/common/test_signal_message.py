"""Signal Message tests for the Cynthus project"""


from uuid import uuid4

from cynthus.messaging.common.signal.lifecycle_action import LifecycleAction
from cynthus.messaging.common.signal.message import SignalMessage
from cynthus.messaging.common.signal.part import SignalPart
from cynthus.messaging.common.signal.payload import SignalPayload


class TestSignalMessage:
    def test_is_subclass_of_signal_part(self):
        """Test that SignalMessage is a subclass of SignalPart"""
        assert issubclass(SignalMessage, SignalPart)

    def test_instance_is_signal_part(self):
        """Test that an instance of SignalMessage is also an instance of SignalPart"""

        message = SignalMessage(
            event_type="test.event",
            lifecycle_action=LifecycleAction.CREATED,
            correlation_id=uuid4(),
            organization_id=uuid4(),
            workspace_id=uuid4(),
            actor_id=uuid4(),
            payload=SignalPayload(schema_version=1)
        )

        assert isinstance(message, SignalPart)
