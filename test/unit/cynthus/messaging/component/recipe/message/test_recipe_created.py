"""Tests for cynthus.messaging.component.recipe.message.recipe_created."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.recipe.message.recipe_created import RecipeCreatedMessage
from cynthus.messaging.component.recipe.payload.recipe_created import RecipeCreatedPayload


def make_message():
    return RecipeCreatedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=RecipeCreatedPayload(recipe_id='r1', owner_id='u1', source='web'),
    )


def test_event_type():
    assert make_message().event_type == 'public.recipe.recipe.created'


def test_round_trips_through_json():
    message = make_message()

    assert RecipeCreatedMessage.model_validate_json(message.model_dump_json()) == message
