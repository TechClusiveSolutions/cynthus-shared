"""Signal Bus Unavailable error for the Cynthus project"""


class SignalBusUnavailable(Exception):
    """The signal bus could not be reached or did not accept a message, even after the one retry on a fresh sender.

    A service that needs the bus to answer a request turns this into "service unavailable" (HTTP 503) for its caller
    instead of an unhandled error. The Service Bus error that caused it is kept as ``__cause__``; its text is not
    copied here because it can name the namespace.
    """
