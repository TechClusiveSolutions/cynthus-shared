"""Signal Contract class for the Cynthus project"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from ..common.signal.base import SignalBase
from ..common.signal.lifecycle_action import LifecycleAction
from ..common.signal.message_base import SignalMessageBase
from ..common.signal.payload import SignalPayload


@dataclass(frozen=True)
class SignalContract:
    """
        Ties one event to one signal, and every payload field to its source

        ``sources`` maps each payload field name to ``data.<field>``, ``resource.<field>``, ``user.<field>``,
        ``tenant.<field>``, ``workspace.<field>`` or ``env.<name>``. See ``docs/signal-generators.md``.
    """

    features: tuple[str, ...]
    event: str
    signal: type[SignalBase]
    message: type[SignalMessageBase]
    payload: type[SignalPayload]
    lifecycle_action: LifecycleAction
    method: str
    sources: Mapping[str, str] = field(hash=False)
