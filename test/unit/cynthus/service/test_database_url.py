from sqlalchemy.engine import make_url

from cynthus.service.database_url import DatabaseUrl


def test_build_uses_the_psycopg_dialect_and_environment_values():
    url = DatabaseUrl({
        'DB_DRIVER': 'postgres', 'DB_HOST': 'db', 'DB_PORT': '5432',
        'DB_NAME': 'cynthus_core', 'DB_USERNAME': 'core_admin', 'DB_PASSWORD': 'p@ss/word',
    }).build()

    assert url.drivername == 'postgresql+psycopg'
    assert (url.host, url.port, url.database, url.username) == ('db', 5432, 'cynthus_core', 'core_admin')
    assert make_url(url.render_as_string(hide_password=False)).password == 'p@ss/word'


def test_build_defaults_host_and_port():
    url = DatabaseUrl({'DB_NAME': 'x'}).build()

    assert (url.host, url.port) == ('db', 5432)


def test_build_reads_the_process_environment_by_default(monkeypatch):
    monkeypatch.setenv('DB_NAME', 'from_env')

    assert DatabaseUrl().build().database == 'from_env'
