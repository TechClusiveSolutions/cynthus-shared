"""Core Signal Topic class for the Cynthus project"""

from .signal_topic import SignalTopic


class CoreSignalTopic(SignalTopic):
    """
        Represents the cynthus-events-topic Azure Service Bus topic

        Domain facts published here are open: any authorized downstream service may consume them.
    """

    name: str = 'cynthus-events-topic'
