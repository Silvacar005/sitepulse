from sitepulse.database import normalize_database_url


def test_normalize_postgresql_url_uses_psycopg_driver():
    assert (
        normalize_database_url("postgresql://user:pass@host:5432/sitepulse")
        == "postgresql+psycopg://user:pass@host:5432/sitepulse"
    )


def test_normalize_legacy_postgres_url_uses_psycopg_driver():
    assert (
        normalize_database_url("postgres://user:pass@host:5432/sitepulse")
        == "postgresql+psycopg://user:pass@host:5432/sitepulse"
    )


def test_sqlite_url_is_unchanged():
    assert normalize_database_url("sqlite:///./sitepulse.db") == "sqlite:///./sitepulse.db"
