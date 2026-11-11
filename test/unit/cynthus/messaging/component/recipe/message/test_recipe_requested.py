"""Tests for cynthus.messaging.component.recipe.message.recipe_requested."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.recipe.message.recipe_requested import RecipeRequestedMessage
from cynthus.messaging.component.recipe.payload.recipe_requested import RecipeRequestedPayload


def make_message():
    return RecipeRequestedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=RecipeRequestedPayload(operation='get'),
    )


def test_event_type():
    assert make_message().event_type == 'public.recipe.recipe.requested'


def test_round_trips_through_json():
    message = make_message()

    assert RecipeRequestedMessage.model_validate_json(message.model_dump_json()) == message
