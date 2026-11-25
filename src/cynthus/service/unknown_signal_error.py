"""Unknown Signal Error class for the Cynthus project"""


class UnknownSignalError(LookupError):
    """No function is registered for a received signal"""

    def __init__(self, signal_name: str) -> None:
        super().__init__(f'No function is registered for the signal {signal_name!r}')

        self.signal_name = signal_name
