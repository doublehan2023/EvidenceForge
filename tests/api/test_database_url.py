from evidenceforge_api.config import to_asyncpg_url


def test_neon_libpq_url_becomes_verified_asyncpg_url() -> None:
    connection = to_asyncpg_url(
        "postgresql://user:password@example.neon.tech/database?sslmode=require&channel_binding=require"
    )

    assert connection.url.startswith("postgresql+asyncpg://")
    assert "channel_binding" not in connection.url
    assert "ssl" in connection.connect_args
    assert connection.connect_args["ssl"].check_hostname is True
