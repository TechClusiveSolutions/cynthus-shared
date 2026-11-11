"""Tests for MealPlanCreatedMessage."""

from datetime import date
from uuid import UUID

import pytest

from cynthus.messaging.common.signal.lifecycle_action import LifecycleAction
from cynthus.messaging.component.meal.message.meal_plan_created import (
    MealPlanCreatedMessage,
)
from cynthus.messaging.component.meal.payload.plan.meal_plan_created import (
    MealPlanCreatedPayload,
)


class TestMealPlanCreatedMessage:
    # ------------------------------------------------------------------
    # event_type
    # ------------------------------------------------------------------

    def test_event_type_is_correct_signal_name(self, meal_plan_created_message):
        msg = meal_plan_created_message()
        assert msg.event_type == "public.meal.plan.created"

    # ------------------------------------------------------------------
    # Default 7-day Astri-assisted plan scenario
    # ------------------------------------------------------------------

    def test_default_lifecycle_action_is_created(self, meal_plan_created_message):
        msg = meal_plan_created_message()
        assert msg.lifecycle_action == LifecycleAction.CREATED

    def test_default_horizon_is_week(self, meal_plan_created_message):
        msg = meal_plan_created_message()
        assert msg.payload.horizon == "week"

    def test_default_dates_span_one_week(self, meal_plan_created_message):
        msg = meal_plan_created_message()
        assert msg.payload.start_date == date(2026, 6, 9)
        assert msg.payload.end_date == date(2026, 6, 15)

    def test_default_meal_count(self, meal_plan_created_message):
        msg = meal_plan_created_message()
        assert msg.payload.meal_count == 21

    def test_default_astri_assisted_is_true(self, meal_plan_created_message):
        msg = meal_plan_created_message()
        assert msg.payload.astri_assisted is True

    # ------------------------------------------------------------------
    # Factory overrides
    # ------------------------------------------------------------------

    def test_manual_plan_not_astri_assisted(self, meal_plan_created_message):
        msg = meal_plan_created_message(astri_assisted=False)
        assert msg.payload.astri_assisted is False

    def test_monthly_plan_override(self, meal_plan_created_message):
        msg = meal_plan_created_message(
            horizon="month",
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 31),
            meal_count=62,
        )
        assert msg.payload.horizon == "month"
        assert msg.payload.start_date == date(2026, 7, 1)
        assert msg.payload.end_date == date(2026, 7, 31)
        assert msg.payload.meal_count == 62

    def test_custom_plan_id(self, meal_plan_created_message):
        msg = meal_plan_created_message(plan_id="plan_specific_abc")
        assert msg.payload.plan_id == "plan_specific_abc"

    def test_custom_organization_id(self, meal_plan_created_message):
        msg = meal_plan_created_message(organization_id="org_acme_corp")
        assert msg.organization_id == "org_acme_corp"

    def test_custom_correlation_id(self, meal_plan_created_message):
        custom = UUID("11111111-2222-3333-4444-555555555555")
        msg = meal_plan_created_message(correlation_id=custom)
        assert msg.correlation_id == custom

    # ------------------------------------------------------------------
    # Immutability
    # ------------------------------------------------------------------

    def test_message_is_frozen(self, meal_plan_created_message):
        msg = meal_plan_created_message()
        with pytest.raises(Exception):
            msg.organization_id = "mutated"  # type: ignore[misc]

    def test_payload_is_frozen(self, meal_plan_created_message):
        msg = meal_plan_created_message()
        with pytest.raises(Exception):
            msg.payload.meal_count = 0  # type: ignore[misc]

    # ------------------------------------------------------------------
    # Type assertions
    # ------------------------------------------------------------------

    def test_message_type(self, meal_plan_created_message):
        msg = meal_plan_created_message()
        assert isinstance(msg, MealPlanCreatedMessage)

    def test_payload_type(self, meal_plan_created_message):
        msg = meal_plan_created_message()
        assert isinstance(msg.payload, MealPlanCreatedPayload)
