"""Tests for cynthus.messaging.test.factory.partner (the package initializer)."""

import importlib

import pytest


@pytest.mark.parametrize('name', [
    'PartnerServiceListRequestedMessageFactory',
    'PartnerServiceListRespondedMessageFactory',
])
def test_package_exports_the_message_factories(name):
    assert hasattr(importlib.import_module('cynthus.messaging.test.factory.partner'), name)
