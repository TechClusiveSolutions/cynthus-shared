"""Engagement, place and attendee unit tests for the Cynthus project (ADR-011)"""

# A fixture is used by naming it as a test argument, which ruff reads as redefining the import
# ruff: noqa: F811

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from cynthus.core.resource import Attendee, Engagement, Place
from cynthus.core.test.factory import (
    AttendeeFactory,
    EngagementFactory,
    PlaceFactory,
    UserFactory,
    WorkspaceFactory,
)
from cynthus.core.test.fixture import engagement, place  # noqa: F401

START = datetime(2026, 12, 5, 18, 0, tzinfo=timezone.utc)


def test_an_engagement_has_a_period_and_may_name_no_place(engagement):
    assert engagement.ends_at > engagement.starts_at
    assert engagement.place is None and engagement.attendees == [] and engagement.materials == []


def test_an_engagement_ends_after_it_starts():
    with pytest.raises(ValidationError, match='ends after it starts'):
        EngagementFactory(starts_at=START, ends_at=START)

    with pytest.raises(ValidationError, match='ends after it starts'):
        EngagementFactory(starts_at=START, ends_at=START - timedelta(hours=1))


def test_an_engagement_uses_a_place_of_its_own_workspace():
    workspace = WorkspaceFactory()

    assert EngagementFactory(workspace=workspace, place=PlaceFactory(workspace=workspace)).place.workspace == workspace

    with pytest.raises(ValidationError, match='place of its own workspace'):
        EngagementFactory(workspace=workspace, place=PlaceFactory())


def test_an_engagement_without_a_place_uses_the_default_place(engagement):
    default = PlaceFactory(workspace=engagement.workspace, is_default=True)

    assert engagement.place_or(default) is default


def test_an_engagement_with_a_place_keeps_it():
    workspace = WorkspaceFactory()
    own = PlaceFactory(workspace=workspace)
    engagement = EngagementFactory(workspace=workspace, place=own)

    assert engagement.place_or(PlaceFactory(workspace=workspace, is_default=True)) is own


def test_with_no_default_either_there_is_no_place(engagement):
    assert engagement.place_or(None) is None


def test_attendees_carry_their_food_preferences():
    guest = AttendeeFactory(name='Sam', food_preferences=['peanut allergy', 'vegetarian'])
    member = Attendee(name='Ada', user_id=UserFactory().id_)

    engagement = EngagementFactory(attendees=[guest, member], materials=['chairs'], notes='Parking is behind the hall')

    assert engagement.attendees[0].food_preferences == ['peanut allergy', 'vegetarian']
    assert engagement.attendees[1].food_preferences == [] and engagement.attendees[1].user_id is not None
    assert engagement.materials == ['chairs'] and engagement.notes == 'Parking is behind the hall'


def test_a_place_is_not_the_default_until_it_is_made_so(place):
    assert place.is_default is False


def test_a_place_holds_at_least_one_person():
    with pytest.raises(ValidationError):
        PlaceFactory(capacity=0)


def test_an_engagement_survives_a_json_round_trip():
    workspace = WorkspaceFactory()
    engagement = EngagementFactory(
        workspace=workspace, place=PlaceFactory(workspace=workspace, capacity=40),
        attendees=[AttendeeFactory(food_preferences=['vegan'])], managers=[UserFactory()])

    assert Engagement.model_validate_json(engagement.model_dump_json()) == engagement
    assert Place.model_validate_json(engagement.place.model_dump_json()) == engagement.place


def test_an_engagement_can_be_soft_deleted(engagement):
    engagement.soft_delete()

    assert engagement.is_deleted
