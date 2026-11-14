"""Unknown Event Error class for the Cynthus project"""


class UnknownEventError(LookupError):
    """Raised when an event or a signal is not in the signal registry"""
