"""Signal Event Mismatch class for the Cynthus project"""


class SignalEventMismatch(ValueError):
    """Raised when a received signal and the verified token claims disagree; the message names the field, never a value"""
