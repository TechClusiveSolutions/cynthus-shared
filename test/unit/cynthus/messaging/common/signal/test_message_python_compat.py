"""Python-version compatibility of cynthus.messaging.common.signal.message (issue #6)."""

import typing_extensions

from cynthus.messaging.common.signal import message as message_module
from cynthus.messaging.common.signal.payload import SignalPayload


def test_payload_type_variable_supports_defaults_on_every_supported_python():
    # `typing.TypeVar(default=...)` exists only from Python 3.13; typing_extensions backports it.
    assert message_module.TypeVar is typing_extensions.TypeVar


def test_payload_type_variable_defaults_to_signal_payload():
    assert message_module.PayloadT.__default__ is SignalPayload
    assert message_module.PayloadT.__bound__ is SignalPayload


def test_message_generic_can_still_be_parameterised():
    assert message_module.SignalMessage[SignalPayload] is not message_module.SignalMessage
