"""Base test class for message classes in the Cynthus project"""



class BaseMessageTest:
    msg_domain: str = 'meal'
    msg_aggregate: str = 'suggestion'
    msg_action: str = 'accepted'


    def test_identity(self):
        # Does the message object have the expected event_type value?
        # Does the message object have the expected lifecycle action value?

        pass

    def test_required_fields(self):
        # Does omitting required fields result in an exception?
        # Does providing invalid values for required fields generate an exception?
        pass

