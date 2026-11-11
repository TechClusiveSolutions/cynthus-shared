"""Tests for cynthus.core.logging."""

import logging as stdlib

import pytest

from cynthus.core import logging as cynthus_logging


@pytest.fixture(autouse=True)
def basic_config(monkeypatch):
    calls = []

    monkeypatch.setattr(cynthus_logging.stdlib, 'basicConfig', lambda **kwargs: calls.append(kwargs))
    monkeypatch.setattr(cynthus_logging, '_configured', False)
    monkeypatch.delenv('LOG_LEVEL', raising=False)
    monkeypatch.delenv('LOG_FORMAT', raising=False)
    monkeypatch.delenv('AZURE_LOG_LEVEL', raising=False)
    monkeypatch.setattr(stdlib.getLogger('azure'), 'level', stdlib.NOTSET)

    return calls


def test_configure_applies_the_defaults(basic_config):
    cynthus_logging.configure()

    assert basic_config == [{
        'level': stdlib.INFO,
        'format': cynthus_logging.DEFAULT_FORMAT,
        'datefmt': cynthus_logging.DEFAULT_DATE_FORMAT,
        'force': False,
    }]


def test_environment_overrides_the_defaults(basic_config, monkeypatch):
    monkeypatch.setenv('LOG_LEVEL', 'debug')
    monkeypatch.setenv('LOG_FORMAT', '%(message)s')

    cynthus_logging.configure()

    assert basic_config[0]['level'] == stdlib.DEBUG
    assert basic_config[0]['format'] == '%(message)s'


def test_arguments_override_the_environment(basic_config, monkeypatch):
    monkeypatch.setenv('LOG_LEVEL', 'debug')
    monkeypatch.setenv('LOG_FORMAT', '%(message)s')

    cynthus_logging.configure(level='ERROR', format='%(name)s', datefmt='%H', force=True)

    assert basic_config[0] == {'level': stdlib.ERROR, 'format': '%(name)s', 'datefmt': '%H', 'force': True}


@pytest.mark.parametrize('level, expected', [(10, 10), ('10', 10), (' warning ', stdlib.WARNING), (stdlib.CRITICAL, 50)])
def test_levels_may_be_names_or_numbers(basic_config, level, expected):
    cynthus_logging.configure(level=level)

    assert basic_config[0]['level'] == expected


def test_an_unknown_level_is_rejected(basic_config):
    with pytest.raises(ValueError):
        cynthus_logging.configure(level='LOUD')

    assert basic_config == []


def test_get_logger_configures_once_and_returns_the_named_logger(basic_config):
    first = cynthus_logging.getLogger('cynthus.test.one')
    second = cynthus_logging.getLogger('cynthus.test.two')

    assert first is stdlib.getLogger('cynthus.test.one')
    assert second.name == 'cynthus.test.two'
    assert len(basic_config) == 1


def test_get_logger_without_a_name_returns_the_root_logger():
    assert cynthus_logging.getLogger() is stdlib.getLogger()


def test_the_standard_names_are_re_exported():
    assert cynthus_logging.INFO == stdlib.INFO
    assert cynthus_logging.DEBUG == stdlib.DEBUG
    assert cynthus_logging.Logger is stdlib.Logger


def test_the_azure_sdk_is_quieted_by_default():
    cynthus_logging.configure()

    assert stdlib.getLogger('azure').level == stdlib.WARNING


def test_the_azure_level_can_be_overridden(monkeypatch):
    monkeypatch.setenv('AZURE_LOG_LEVEL', 'debug')

    cynthus_logging.configure()

    assert stdlib.getLogger('azure').level == stdlib.DEBUG
