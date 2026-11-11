"""Meal Suggestion Message tests for the Cynthus project"""

import re
from uuid import UUID, uuid4

import pytest

from cynthus.messaging.common.signal import (
    DecisionReason,
    EnergyLevel,
    LifecycleAction,
    PublicMealSuggestionAcceptedSignal,
    PublicMealSuggestionGeneratedSignal,
    PublicMealSuggestionRejectedSignal,
    PublicMealSuggestionRequestedSignal,
    SignalTriggerType,
)
from cynthus.messaging.component.meal.message import (
    MealSuggestionAcceptedMessage,
    MealSuggestionGeneratedMessage,
    MealSuggestionRejectedMessage,
    MealSuggestionRequestedMessage,
)
from cynthus.messaging.component.meal.payload import (
    MealSuggestionRejectedPayload,
)
from cynthus.messaging.test.factory.meal import (
    MealSuggestionAcceptedMessageFactory,
    MealSuggestionRejectedMessageFactory,
    MealSuggestionRequestedMessageFactory,
)


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
    # Defaults / lifecycle
    # ------------------------------------------------------------------

    def test_accepted_default_reason_is_not_specified(self, meal_suggestion_accepted_message: MealSuggestionAcceptedMessage):
        assert meal_suggestion_accepted_message.payload.reason == DecisionReason.NOT_SPECIFIED


    def test_rejected_default_reason_is_not_specified(self, meal_suggestion_rejected_message: MealSuggestionRejectedMessage):
        assert meal_suggestion_rejected_message.payload.reason == DecisionReason.NOT_SPECIFIED


    def test_accepted_lifecycle_action_is_updated(self, meal_suggestion_accepted_message: MealSuggestionAcceptedMessage):
        assert meal_suggestion_accepted_message.lifecycle_action == LifecycleAction.UPDATED


    def test_generated_lifecycle_action_is_created(self, meal_suggestion_generated_message: MealSuggestionGeneratedMessage):
        assert meal_suggestion_generated_message.lifecycle_action == LifecycleAction.CREATED


    def test_rejected_lifecycle_action_is_updated(self, meal_suggestion_rejected_message: MealSuggestionRejectedMessage):
        assert meal_suggestion_rejected_message.lifecycle_action == LifecycleAction.UPDATED


    def test_requested_lifecycle_action_is_created(self, meal_suggestion_requested_message: MealSuggestionRequestedMessage):
        assert meal_suggestion_requested_message.lifecycle_action == LifecycleAction.CREATED


    def test_accepted_payload_ids_present(self, meal_suggestion_accepted_message: MealSuggestionAcceptedMessage):
        pattern = re.compile(r'^[\w\d]{8}-[\d\w]{4}-[\d\w]{4}-[\d\w]{4}-[\d\w]{12}$')

        assert re.match(pattern, str(meal_suggestion_accepted_message.payload.suggestion_id))
        assert re.match(pattern, str(meal_suggestion_accepted_message.payload.context_bundle_id))


    def test_generated_payload_ids_present(self, meal_suggestion_generated_message: MealSuggestionGeneratedMessage):
        pattern = re.compile(r'^[\w\d]{8}-[\d\w]{4}-[\d\w]{4}-[\d\w]{4}-[\d\w]{12}$')

        assert re.match(pattern, str(meal_suggestion_generated_message.payload.suggestion_id))
        assert re.match(pattern, str(meal_suggestion_generated_message.payload.context_bundle_id))


    def test_rejected_payload_ids_present(self, meal_suggestion_rejected_message: MealSuggestionRejectedMessage):
        pattern = re.compile(r'^[\w\d]{8}-[\d\w]{4}-[\d\w]{4}-[\d\w]{4}-[\d\w]{12}$')

        assert re.match(pattern, str(meal_suggestion_rejected_message.payload.suggestion_id))
        assert re.match(pattern, str(meal_suggestion_rejected_message.payload.context_bundle_id))


    def test_requested_payload_ids_present(self, meal_suggestion_requested_message: MealSuggestionRequestedMessage):
        pattern = re.compile(r'^[\w\d]{8}-[\d\w]{4}-[\d\w]{4}-[\d\w]{4}-[\d\w]{12}$')

        assert re.match(pattern, str(meal_suggestion_requested_message.payload.context_bundle_id))


    # ------------------------------------------------------------------
    # Factory overrides
    # ------------------------------------------------------------------

    def test_accepted_reason_can_be_overridden(self):
        msg = MealSuggestionAcceptedMessageFactory(payload__reason=DecisionReason.SOUNDS_YUMMY)

        assert msg.payload.reason != DecisionReason.NOT_SPECIFIED


    def test_rejected_reason_can_be_overridden(self):
        msg = MealSuggestionRejectedMessageFactory(payload__reason=DecisionReason.ALLERGIC_TO_INGREDIENT)

        assert msg.payload.reason != DecisionReason.NOT_SPECIFIED


    def test_requested_trigger_can_be_overridden(self):
        msg = MealSuggestionRequestedMessageFactory(payload__trigger=SignalTriggerType.TIMER_EXPIRED)

        assert msg.payload.trigger != SignalTriggerType.ACTION_PERFORMED


    def test_requested_energy_level_can_be_overridden(self):
        msg = MealSuggestionRequestedMessageFactory(payload__energy_level=EnergyLevel.HIGH)

        assert msg.payload.energy_level != EnergyLevel.MEDIUM


    def test_accepted_reason_can_be_none(self):
        """Users can accept without giving a reason — reason is optional."""
        msg = MealSuggestionAcceptedMessageFactory(payload__reason=None)

        assert msg.payload.reason is None


    def test_rejected_reason_can_be_none(self):
        """Users can reject without giving a reason — reason is optional."""
        msg = MealSuggestionRejectedMessageFactory(payload__reason=None)

        assert msg.payload.reason is None


    def test_custom_actor_id(self):
        id_ = uuid4()
        msg = MealSuggestionRejectedMessageFactory(actor_id=id_)
        assert msg.actor_id == id_


    def test_custom_correlation_id(self):
        custom = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        msg = MealSuggestionRejectedMessageFactory(correlation_id=custom)
        assert msg.correlation_id == custom

    # ------------------------------------------------------------------
    # Immutability
    # ------------------------------------------------------------------

    def test_message_is_frozen(self, meal_suggestion_rejected_message):
        with pytest.raises(Exception):  # ValidationError or TypeError from frozen model
            meal_suggestion_rejected_message.actor_id = "hacker"  # type: ignore[misc]

    def test_payload_is_frozen(self, meal_suggestion_rejected_message):
        with pytest.raises(Exception):
            meal_suggestion_rejected_message.payload.reason = "mutated"  # type: ignore[misc]

    # ------------------------------------------------------------------
    # Type assertions
    # ------------------------------------------------------------------

    def test_message_type(self, meal_suggestion_rejected_message):
        assert isinstance(meal_suggestion_rejected_message, MealSuggestionRejectedMessage)

    def test_payload_type(self, meal_suggestion_rejected_message):
        assert isinstance(meal_suggestion_rejected_message.payload, MealSuggestionRejectedPayload)
