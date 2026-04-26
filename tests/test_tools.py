from __future__ import annotations

from pathlib import Path

import pytest

from src.bauamt_mcp.seed import seed_database
from src.bauamt_mcp.tools import (
    get_kpi_summary,
    get_permit_details,
    prepare_data_entry,
    search_permits,
)


@pytest.fixture()
def seeded_temp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    db_path = tmp_path / "bauamt_permits_test.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    seed_database(count=50)
    return db_path


def test_search_permits_finds_known_demo_record(seeded_temp_db: Path) -> None:
    results = search_permits(address="Hauptstraße 12", submitted_year=2024)

    assert len(results) >= 1
    assert results[0]["id"] == "BG-2024-0847"
    assert results[0]["applicant_name"] == "Müller Bau GmbH"
    assert results[0]["status"] == "unterlagen_fehlen"


def test_get_permit_details_returns_missing_documents(seeded_temp_db: Path) -> None:
    permit = get_permit_details("BG-2024-0847")

    assert permit["found"] is True
    assert permit["id"] == "BG-2024-0847"
    assert permit["permit_type"] == "Umbau"
    assert permit["missing_documents"] == [
        "Brandschutznachweis",
        "Statiknachweis",
    ]
    assert permit["assigned_clerk"] == "Frau Schneider"
    assert "days_until_deadline" in permit
    assert "is_overdue" in permit
    assert "overdue_by_days" in permit


def test_get_permit_details_handles_unknown_id(seeded_temp_db: Path) -> None:
    permit = get_permit_details("BG-DOES-NOT-EXIST")

    assert permit["found"] is False
    assert permit["permit_id"] == "BG-DOES-NOT-EXIST"


def test_get_kpi_summary_returns_expected_contract(seeded_temp_db: Path) -> None:
    summary = get_kpi_summary(
        office_id="BAUAMT-LE-01",
        start_date="2024-01-01",
        end_date="2026-12-31",
    )

    assert summary["office_id"] == "BAUAMT-LE-01"
    assert summary["date_range"]["start_date"] == "2024-01-01"
    assert summary["date_range"]["end_date"] == "2026-12-31"
    assert summary["total_permits"] >= 1
    assert "pending_permits" in summary
    assert "overdue_more_than_30_days" in summary
    assert "missing_documents_cases" in summary
    assert "average_nominal_processing_days" in summary


def test_prepare_data_entry_is_draft_only_and_rejects_unknown_fields(
    seeded_temp_db: Path,
) -> None:
    draft = prepare_data_entry(
        "BG-2024-0847",
        {
            "status": "genehmigungsbereit",
            "approval_date": "2026-04-26",
            "clerk_note": "Alle erforderlichen Unterlagen liegen vor.",
            "dangerous_sql": "DROP TABLE permits",
        },
    )

    assert draft["prepared"] is True
    assert draft["permit_id"] == "BG-2024-0847"
    assert draft["draft_entry"]["status"] == "genehmigungsbereit"
    assert draft["draft_entry"]["approval_date"] == "2026-04-26"
    assert draft["rejected_fields"] == ["dangerous_sql"]
    assert draft["safety"]["database_updated"] is False
    assert draft["safety"]["requires_human_confirmation"] is True


def test_prepare_data_entry_handles_unknown_permit(seeded_temp_db: Path) -> None:
    draft = prepare_data_entry(
        "BG-DOES-NOT-EXIST",
        {
            "status": "genehmigungsbereit",
        },
    )

    assert draft["prepared"] is False
    assert draft["database_updated"] is False