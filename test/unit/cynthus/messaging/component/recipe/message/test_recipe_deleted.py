"""Tests for cynthus.messaging.component.recipe.message.recipe_deleted."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.recipe.message.recipe_deleted import RecipeDeletedMessage
from cynthus.messaging.component.recipe.payload.recipe_deleted import RecipeDeletedPayload


def make_message():
    return RecipeDeletedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=RecipeDeletedPayload(recipe_id='r1', owner_id='u1'),
    )


def test_event_type():
    assert make_message().event_type == 'public.recipe.recipe.deleted'


def test_round_trips_through_json():
    message = make_message()

    assert RecipeDeletedMessage.model_validate_json(message.model_dump_json()) == message
