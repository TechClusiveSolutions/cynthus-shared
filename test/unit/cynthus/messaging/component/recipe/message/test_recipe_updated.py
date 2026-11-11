"""Tests for cynthus.messaging.component.recipe.message.recipe_updated."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.recipe.message.recipe_updated import RecipeUpdatedMessage
from cynthus.messaging.component.recipe.payload.recipe_updated import RecipeUpdatedPayload


def make_message():
    return RecipeUpdatedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=RecipeUpdatedPayload(recipe_id='r1', owner_id='u1', changed=['title']),
    )


def test_event_type():
    assert make_message().event_type == 'public.recipe.recipe.updated'


def test_round_trips_through_json():
    message = make_message()

    assert RecipeUpdatedMessage.model_validate_json(message.model_dump_json()) == message
