"""Tests for cynthus.messaging.component.recipe.message.recipe_responded."""

from uuid import uuid4

from cynthus.messaging.common import LifecycleAction
from cynthus.messaging.component.recipe.message.recipe_responded import RecipeRespondedMessage
from cynthus.messaging.component.recipe.payload.recipe_responded import RecipeRespondedPayload


def make_message():
    return RecipeRespondedMessage(
        lifecycle_action=LifecycleAction.UPDATED,
        correlation_id=uuid4(),
        organization_id=uuid4(),
        workspace_id=uuid4(),
        actor_id=uuid4(),
        payload=RecipeRespondedPayload(operation='get', status=200),
    )


def test_event_type():
    assert make_message().event_type == 'public.recipe.recipe.responded'


def test_round_trips_through_json():
    message = make_message()

    assert RecipeRespondedMessage.model_validate_json(message.model_dump_json()) == message
