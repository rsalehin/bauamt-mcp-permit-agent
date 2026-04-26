from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.bauamt_mcp.db import initialize_database
from src.bauamt_mcp.tools import (
    get_kpi_summary as domain_get_kpi_summary,
    get_permit_details as domain_get_permit_details,
    prepare_data_entry as domain_prepare_data_entry,
    search_permits as domain_search_permits,
)

logging.basicConfig(level=logging.INFO)

mcp = FastMCP("bauamt-permit-agent")


@mcp.tool()
def search_permits(
    applicant_name: str | None = None,
    address: str | None = None,
    status_filter: str | None = None,
    submitted_year: int | None = None,
) -> list[dict[str, Any]]:
    """
    Search German municipal building permits by applicant, address, status, or submitted year.

    Example German clerk requests:
    - Finde alle offenen Bauanträge für Hauptstraße 12 aus dem Jahr 2024.
    - Suche alle Anträge von Müller Bau GmbH.
    - Zeige alle überfälligen Bauanträge.
    """
    return domain_search_permits(
        applicant_name=applicant_name,
        address=address,
        status_filter=status_filter,
        submitted_year=submitted_year,
    )


@mcp.tool()
def get_permit_details(permit_id: str) -> dict[str, Any]:
    """
    Get full details for one German building permit.

    Use this when the clerk asks about missing documents, permit status,
    assigned clerk, deadline, applicant, address, or estimated project cost.

    Example:
    - Welche Unterlagen fehlen noch für BG-2024-0847?
    """
    return domain_get_permit_details(permit_id)


@mcp.tool()
def get_kpi_summary(
    office_id: str,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    """
    Calculate permit-processing KPIs for a Bauamt office in a date range.

    Dates must use ISO format: YYYY-MM-DD.

    Example:
    - Wie viele Anträge im BAUAMT-LE-01 sind zwischen 2024-01-01 und 2026-12-31 mehr als 30 Tage überfällig?
    """
    return domain_get_kpi_summary(
        office_id=office_id,
        start_date=start_date,
        end_date=end_date,
    )


@mcp.tool()
def prepare_data_entry(
    permit_id: str,
    field_updates: dict[str, Any],
) -> dict[str, Any]:
    """
    Prepare a draft data-entry update for a building permit.

    Safety rule:
    This tool never writes to the database. It only returns a structured draft
    that a human clerk must review and approve.

    Example:
    - Bereite eine Dateneingabe vor, um BG-2024-0847 als genehmigungsbereit zu markieren. Nicht speichern.
    """
    return domain_prepare_data_entry(
        permit_id=permit_id,
        field_updates=field_updates,
    )


def main() -> None:
    initialize_database()
    mcp.run()


if __name__ == "__main__":
    main()