"""Meal Suggestion Message tests for the Cynthus project"""

from uuid import UUID

import pytest

from cynthus.messaging.common.signal import (
    LifecycleAction,
    PublicMealSuggestionAcceptedSignal,
    PublicMealSuggestionGeneratedSignal,
    PublicMealSuggestionRejectedSignal,
    PublicMealSuggestionRequestedSignal,
)
from cynthus.messaging.component.meal.message import (
    MealSuggestionAcceptedMessage,
    MealSuggestionGeneratedMessage,
    MealSuggestionRejectedMessage,
    MealSuggestionRequestedMessage,
)
from cynthus.messaging.component.meal.payload import MealSuggestionRejectedPayload


class TestMealMessages:
    # ------------------------------------------------------------------
    # event_type
    # ------------------------------------------------------------------

    def test_accepted_event_type_is_correct_signal_name(self, meal_suggestion_accepted_message: MealSuggestionAcceptedMessage):
        assert meal_suggestion_accepted_message.event_type == PublicMealSuggestionAcceptedSignal.name


    def test_generated_event_type_is_correct_signal_name(self, meal_suggestion_generated_message: MealSuggestionGeneratedMessage):
        assert meal_suggestion_generated_message.event_type == PublicMealSuggestionGeneratedSignal.name


    def test_rejected_event_type_is_correct_signal_name(self, meal_suggestion_rejected_message: MealSuggestionRejectedMessage):
        assert meal_suggestion_rejected_message.event_type == PublicMealSuggestionRejectedSignal.name


    def test_requested_event_type_is_correct_signal_name(self, meal_suggestion_requested_message: MealSuggestionRequestedMessage):
        assert meal_suggestion_requested_message.event_type == PublicMealSuggestionRequestedSignal.name


# ------------------------------------------------------------------
    # Default "I'm too tired to cook" scenario
    # ------------------------------------------------------------------

    def test_default_reason_is_too_tired(self, meal_suggestion_rejected_message):
        msg = meal_suggestion_rejected_message()
        assert msg.payload.reason == "I'm too tired to cook"

    def test_default_lifecycle_action_is_deleted(self, meal_suggestion_rejected_message):
        """A rejection removes the suggestion from the user's active session."""
        msg = meal_suggestion_rejected_message()
        assert msg.lifecycle_action == LifecycleAction.DELETED

    def test_default_payload_ids_are_present(self, meal_suggestion_rejected_message):
        msg = meal_suggestion_rejected_message()
        assert msg.payload.suggestion_id == "sug_01TIRED2COOK000001"
        assert msg.payload.context_bundle_id == "ctx_01TIRED2COOK000001"

    # ------------------------------------------------------------------
    # Factory overrides
    # ------------------------------------------------------------------

    def test_reason_can_be_overridden(self, meal_suggestion_rejected_message):
        msg = meal_suggestion_rejected_message(reason="Too spicy for me")
        assert msg.payload.reason == "Too spicy for me"

    def test_reason_can_be_none(self, meal_suggestion_rejected_message):
        """Users can reject without giving a reason — reason is optional."""
        msg = meal_suggestion_rejected_message(reason=None)
        assert msg.payload.reason is None

    def test_suggestion_id_can_be_overridden(self, meal_suggestion_rejected_message):
        msg = meal_suggestion_rejected_message(suggestion_id="sug_custom_abc")
        assert msg.payload.suggestion_id == "sug_custom_abc"

    def test_custom_actor_id(self, meal_suggestion_rejected_message):
        msg = meal_suggestion_rejected_message(actor_id="usr_01HSPECIFIC")
        assert msg.actor_id == "usr_01HSPECIFIC"

    def test_custom_correlation_id(self, meal_suggestion_rejected_message):
        custom = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        msg = meal_suggestion_rejected_message(correlation_id=custom)
        assert msg.correlation_id == custom

    # ------------------------------------------------------------------
    # Immutability
    # ------------------------------------------------------------------

    def test_message_is_frozen(self, meal_suggestion_rejected_message):
        msg = meal_suggestion_rejected_message()
        with pytest.raises(Exception):  # ValidationError or TypeError from frozen model
            msg.actor_id = "hacker"  # type: ignore[misc]

    def test_payload_is_frozen(self, meal_suggestion_rejected_message):
        msg = meal_suggestion_rejected_message()
        with pytest.raises(Exception):
            msg.payload.reason = "mutated"  # type: ignore[misc]

    # ------------------------------------------------------------------
    # Type assertions
    # ------------------------------------------------------------------

    def test_message_type(self, meal_suggestion_rejected_message):
        msg = meal_suggestion_rejected_message()
        assert isinstance(msg, MealSuggestionRejectedMessage)

    def test_payload_type(self, meal_suggestion_rejected_message):
        msg = meal_suggestion_rejected_message()
        assert isinstance(msg.payload, MealSuggestionRejectedPayload)
