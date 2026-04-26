# MCP Inspector Test Guide

## Purpose

Use MCP Inspector to verify that the Bauamt MCP server exposes the expected tools and that each tool can be called independently of Claude Desktop.

MCP Inspector is useful as a fallback/debugging tool before an interview demo.

## Prerequisites

- Node.js installed
- Python virtual environment created
- Python dependencies installed
- Demo database seeded

## Pre-check

From the project root, run:

python -m src.bauamt_mcp.seed
pytest tests/test_tools.py

Expected:

6 passed

## Start MCP Inspector

From the project root, run:

npx @modelcontextprotocol/inspector .\.venv\Scripts\python.exe -m src.bauamt_mcp.server

MCP Inspector should open a local browser UI.

## Expected tools

The Inspector should show these tools:

- search_permits
- get_permit_details
- get_kpi_summary
- prepare_data_entry

## Test call 1 — search_permits

Tool:

search_permits

Arguments:

{
  "address": "Hauptstraße 12",
  "submitted_year": 2024
}

Expected result includes:

- BG-2024-0847
- Müller Bau GmbH
- Hauptstraße 12, Leipzig
- unterlagen_fehlen

## Test call 2 — get_permit_details

Tool:

get_permit_details

Arguments:

{
  "permit_id": "BG-2024-0847"
}

Expected result includes:

- Brandschutznachweis
- Statiknachweis
- Frau Schneider

## Test call 3 — get_kpi_summary

Tool:

get_kpi_summary

Arguments:

{
  "office_id": "BAUAMT-LE-01",
  "start_date": "2024-01-01",
  "end_date": "2026-12-31"
}

Expected result includes:

- total_permits
- pending_permits
- overdue_more_than_30_days
- missing_documents_cases
- average_nominal_processing_days

## Test call 4 — prepare_data_entry

Tool:

prepare_data_entry

Arguments:

{
  "permit_id": "BG-2024-0847",
  "field_updates": {
    "status": "genehmigungsbereit",
    "approval_date": "2026-04-26",
    "clerk_note": "Alle erforderlichen Unterlagen liegen vor.",
    "dangerous_sql": "DROP TABLE permits"
  }
}

Expected safety result:

- prepared: true
- database_updated: false
- requires_human_confirmation: true
- rejected_fields contains dangerous_sql

## Interview use

If Claude Desktop integration fails, open MCP Inspector and show that the server exposes the tools correctly.

Then run the smoke demo:

python -m src.bauamt_mcp.smoke_demo

This proves the backend/tool layer works even if the Claude Desktop client setup is not available.