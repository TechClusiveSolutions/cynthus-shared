"""EventRequestAnswerReason class unit tests for the Cynthus project"""

from cynthus.core.event import EventRequestAnswerReason


def test_access_permitted_exists_with_its_value():
    assert EventRequestAnswerReason.ACCESS_PERMITTED.value == 'access_permitted'
    assert EventRequestAnswerReason('access_permitted') is EventRequestAnswerReason.ACCESS_PERMITTED


def test_access_permitted_compares_equal_to_plain_text():
    assert EventRequestAnswerReason.ACCESS_PERMITTED == 'access_permitted'


def test_permitted_stays_distinct_from_access_permitted():
    assert EventRequestAnswerReason.PERMITTED == 'permitted'
    assert EventRequestAnswerReason.PERMITTED is not EventRequestAnswerReason.ACCESS_PERMITTED


def test_the_existing_reasons_are_unchanged():
    assert {reason.value for reason in EventRequestAnswerReason} >= {
        'permitted', 'approval_required', 'approval_granted', 'approval_denied', 'insufficient_privileges', 'expired',
        'access_permitted',
    }
