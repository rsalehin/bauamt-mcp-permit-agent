from __future__ import annotations

import json
from datetime import date
from typing import Any

from src.bauamt_mcp.db import get_connection


def _row_to_dict(row: Any) -> dict[str, Any]:
    data = dict(row)

    if "missing_documents" in data:
        try:
            data["missing_documents"] = json.loads(data["missing_documents"])
        except json.JSONDecodeError:
            data["missing_documents"] = []

    return data


def search_permits(
    applicant_name: str | None = None,
    address: str | None = None,
    status_filter: str | None = None,
    submitted_year: int | None = None,
) -> list[dict[str, Any]]:
    """
    Search German municipal building permits by applicant, address, status, and submitted year.
    Use this when a clerk asks to find permits matching a person, company, address, status, or year.
    """
    query = """
        SELECT
            id,
            applicant_name,
            address,
            permit_type,
            status,
            submitted_date,
            deadline,
            assigned_clerk,
            office_id
        FROM permits
        WHERE 1 = 1
    """
    params: list[Any] = []

    if applicant_name:
        query += " AND lower(applicant_name) LIKE lower(?)"
        params.append(f"%{applicant_name}%")

    if address:
        query += " AND lower(address) LIKE lower(?)"
        params.append(f"%{address}%")

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    if submitted_year:
        query += " AND substr(submitted_date, 1, 4) = ?"
        params.append(str(submitted_year))

    query += " ORDER BY submitted_date DESC LIMIT 20"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return [_row_to_dict(row) for row in rows]


def get_permit_details(permit_id: str) -> dict[str, Any]:
    """
    Get full details for one German building permit, including missing documents and deadline status.
    Use this when a clerk asks what is missing, who is assigned, or what the current status is.
    """
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                id,
                applicant_name,
                address,
                permit_type,
                status,
                submitted_date,
                deadline,
                missing_documents,
                assigned_clerk,
                office_id,
                estimated_cost_eur,
                last_updated
            FROM permits
            WHERE id = ?
            """,
            (permit_id,),
        ).fetchone()

    if row is None:
        return {
            "found": False,
            "permit_id": permit_id,
            "message": "No permit found with this ID.",
        }

    data = _row_to_dict(row)
    deadline = date.fromisoformat(data["deadline"])
    today = date.today()
    data["found"] = True
    data["days_until_deadline"] = (deadline - today).days
    data["is_overdue"] = deadline < today
    data["overdue_by_days"] = max((today - deadline).days, 0)

    return data


def get_kpi_summary(
    office_id: str,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    """
    Calculate KPI summary for a Bauamt office in a date range.
    Use this for reporting questions like overdue permits, pending cases, missing documents, and average processing time.
    Dates must be ISO format: YYYY-MM-DD.
    """
    with get_connection() as conn:
        total = conn.execute(
            """
            SELECT COUNT(*)
            FROM permits
            WHERE office_id = ?
              AND submitted_date BETWEEN ? AND ?
            """,
            (office_id, start_date, end_date),
        ).fetchone()[0]

        pending = conn.execute(
            """
            SELECT COUNT(*)
            FROM permits
            WHERE office_id = ?
              AND submitted_date BETWEEN ? AND ?
              AND status IN ('eingereicht', 'in_prüfung', 'unterlagen_fehlen', 'genehmigungsbereit', 'überfällig')
            """,
            (office_id, start_date, end_date),
        ).fetchone()[0]

        overdue_more_than_30_days = conn.execute(
            """
            SELECT COUNT(*)
            FROM permits
            WHERE office_id = ?
              AND submitted_date BETWEEN ? AND ?
              AND julianday('now') - julianday(deadline) > 30
            """,
            (office_id, start_date, end_date),
        ).fetchone()[0]

        missing_documents_cases = conn.execute(
            """
            SELECT COUNT(*)
            FROM permits
            WHERE office_id = ?
              AND submitted_date BETWEEN ? AND ?
              AND missing_documents != '[]'
            """,
            (office_id, start_date, end_date),
        ).fetchone()[0]

        avg_processing_days = conn.execute(
            """
            SELECT AVG(julianday(deadline) - julianday(submitted_date))
            FROM permits
            WHERE office_id = ?
              AND submitted_date BETWEEN ? AND ?
            """,
            (office_id, start_date, end_date),
        ).fetchone()[0]

    return {
        "office_id": office_id,
        "date_range": {
            "start_date": start_date,
            "end_date": end_date,
        },
        "total_permits": total,
        "pending_permits": pending,
        "overdue_more_than_30_days": overdue_more_than_30_days,
        "missing_documents_cases": missing_documents_cases,
        "average_nominal_processing_days": round(avg_processing_days or 0, 1),
    }


def prepare_data_entry(
    permit_id: str,
    field_updates: dict[str, Any],
) -> dict[str, Any]:
    """
    Prepare a draft data-entry update for a building permit.
    This tool must not write to the database. It only returns a reviewable draft for a human clerk.
    """
    allowed_fields = {
        "status",
        "approval_date",
        "clerk_note",
        "assigned_clerk",
        "missing_documents",
    }

    rejected_fields = sorted(set(field_updates) - allowed_fields)
    accepted_updates = {
        key: value for key, value in field_updates.items() if key in allowed_fields
    }

    permit = get_permit_details(permit_id)

    if not permit.get("found"):
        return {
            "prepared": False,
            "permit_id": permit_id,
            "message": "Cannot prepare data entry because the permit was not found.",
            "database_updated": False,
        }

    return {
        "prepared": True,
        "permit_id": permit_id,
        "current_status": permit["status"],
        "draft_entry": accepted_updates,
        "rejected_fields": rejected_fields,
        "safety": {
            "database_updated": False,
            "requires_human_confirmation": True,
            "reason": "MCP tool is intentionally draft-only for write-like operations.",
        },
    }