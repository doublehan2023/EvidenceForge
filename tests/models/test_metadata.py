import evidenceforge_api.models  # noqa: F401
from evidenceforge_api.db.base import Base


def test_all_phase_zero_tables_are_registered() -> None:
    expected = {
        "users",
        "workspaces",
        "memberships",
        "sessions",
        "research_runs",
        "sources",
        "evidence_chunks",
        "claims",
        "citations",
        "reports",
        "budgets",
        "model_call_records",
    }
    assert expected.issubset(Base.metadata.tables)
