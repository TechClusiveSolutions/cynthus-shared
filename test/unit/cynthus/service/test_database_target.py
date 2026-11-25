import pytest

from cynthus.service.database_target import DatabaseTarget

ENVIRONMENT = {
    'DB_HOST': 'prod-db', 'DB_PORT': '5433', 'DB_NAME': 'cynthus_partner',
    'DB_USERNAME': 'partner_admin', 'DB_PASSWORD': 'prod-secret',
    'TEST_DB_HOST': 'test-db', 'TEST_DB_NAME': 'cynthus_partner_test',
    'TEST_DB_USERNAME': 'partner_test', 'TEST_DB_PASSWORD': 'test-secret',
    'DEV_DB_NAME': 'cynthus_partner_dev', 'DEV_DB_USERNAME': 'partner_dev', 'DEV_DB_PASSWORD': 'dev-secret',
}


def parts(target):
    return target.url.host, target.url.port, target.url.database, target.url.username, target.schema


def test_production_reads_the_unprefixed_variables():
    target = DatabaseTarget.resolve('production', 'partner', ENVIRONMENT)

    assert parts(target) == ('prod-db', 5433, 'cynthus_partner', 'partner_admin', 'partner')
    assert target.url.password == 'prod-secret'


def test_testing_reads_the_test_variables_and_a_test_schema():
    target = DatabaseTarget.resolve('testing', 'partner', ENVIRONMENT)

    assert parts(target) == ('test-db', 5432, 'cynthus_partner_test', 'partner_test', 'test_partner')


def test_development_reads_the_dev_variables_and_defaults_host_and_port():
    target = DatabaseTarget.resolve('development', 'partner', ENVIRONMENT)

    assert parts(target) == ('db', 5432, 'cynthus_partner_dev', 'partner_dev', 'partner')


def test_a_missing_environment_means_development():
    assert DatabaseTarget.resolve(None, 'partner', ENVIRONMENT) == DatabaseTarget.resolve('development', 'partner', ENVIRONMENT)


def test_the_environment_name_ignores_case_and_spaces():
    assert DatabaseTarget.resolve(' Production ', 'partner', ENVIRONMENT).url.host == 'prod-db'


def test_a_schema_variable_overrides_the_default_schema():
    target = DatabaseTarget.resolve('development', 'partner', {**ENVIRONMENT, 'DEV_DB_SCHEMA': 'sandbox'})

    assert target.schema == 'sandbox'


def test_an_unknown_environment_is_refused_not_defaulted_to_production():
    with pytest.raises(ValueError, match='Unknown environment'):
        DatabaseTarget.resolve('staging', 'partner', ENVIRONMENT)


def test_a_missing_variable_is_named():
    values = {key: value for key, value in ENVIRONMENT.items() if key != 'TEST_DB_PASSWORD'}

    with pytest.raises(ValueError, match='TEST_DB_PASSWORD'):
        DatabaseTarget.resolve('testing', 'partner', values)


@pytest.mark.parametrize('service', ['', 'Partner', 'part ner', 'partner;drop', '1partner'])
def test_a_bad_service_name_is_refused(service):
    with pytest.raises(ValueError, match='Invalid service name'):
        DatabaseTarget.resolve('production', service, ENVIRONMENT)


def test_a_bad_schema_name_is_refused():
    with pytest.raises(ValueError, match='Invalid schema name'):
        DatabaseTarget.resolve('production', 'partner', {**ENVIRONMENT, 'DB_SCHEMA': 'a b'})


def test_the_process_environment_is_read_by_default(monkeypatch):
    for key, value in ENVIRONMENT.items():
        monkeypatch.setenv(key, value)

    assert DatabaseTarget.resolve('testing', 'partner').url.username == 'partner_test'


def test_equal_targets_are_equal_and_hashable():
    first = DatabaseTarget.resolve('production', 'partner', ENVIRONMENT)
    second = DatabaseTarget.resolve('production', 'partner', ENVIRONMENT)

    assert first == second
    assert len({first, second}) == 1
