from __future__ import annotations

import json

from src.bauamt_mcp.seed import seed_database
from src.bauamt_mcp.tools import (
    get_kpi_summary,
    get_permit_details,
    prepare_data_entry,
    search_permits,
)


def print_section(title: str, payload: object) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    seed_database(count=50)

    print_section(
        "1. Search permits: Hauptstraße 12, submitted in 2024",
        search_permits(address="Hauptstraße 12", submitted_year=2024),
    )

    print_section(
        "2. Permit details: missing documents for BG-2024-0847",
        get_permit_details("BG-2024-0847"),
    )

    print_section(
        "3. KPI summary: BAUAMT-LE-01 from 2024-01-01 to 2026-12-31",
        get_kpi_summary(
            office_id="BAUAMT-LE-01",
            start_date="2024-01-01",
            end_date="2026-12-31",
        ),
    )

    print_section(
        "4. Draft-only data entry: mark BG-2024-0847 as ready for approval",
        prepare_data_entry(
            "BG-2024-0847",
            {
                "status": "genehmigungsbereit",
                "approval_date": "2026-04-26",
                "clerk_note": "Alle erforderlichen Unterlagen liegen vor.",
                "dangerous_sql": "DROP TABLE permits",
            },
        ),
    )


if __name__ == "__main__":
    main()