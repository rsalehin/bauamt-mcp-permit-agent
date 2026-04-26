# Bauamt MCP Permit Agent

A local MCP server that exposes a synthetic German municipal building-permit system to Claude.

## Demo thesis

A Bauamt clerk normally has to open a permit-management system, search for a permit, inspect missing documents, copy KPI values into reports, and prepare form entries manually.

This project shows how the same workflow can be exposed through MCP tools so Claude can interact with the domain system directly from German natural language.

## What Claude can do

- Search building permits
- Retrieve permit details
- Show missing documents
- Calculate office-level KPIs
- Prepare draft-only data entries
- Keep write-like actions behind human approval

## MCP tools

### search_permits

Search permits by applicant name, address, status, or submitted year.

Example:

Finde alle Bauanträge für Hauptstraße 12 aus dem Jahr 2024.

### get_permit_details

Retrieve full details for one permit.

Example:

Welche Unterlagen fehlen noch für BG-2024-0847?

### get_kpi_summary

Calculate KPI summaries for an office and date range.

Example:

Wie viele Anträge im BAUAMT-LE-01 sind zwischen 2024-01-01 und 2026-12-31 mehr als 30 Tage überfällig?

### prepare_data_entry

Prepare a draft data-entry update without writing to the database.

Example:

Bereite eine Dateneingabe vor, um BG-2024-0847 als genehmigungsbereit zu markieren. Nicht speichern.

## Safety model

Claude does not receive arbitrary SQL access.

The MCP server exposes only narrow domain tools. The write-like tool, prepare_data_entry, is intentionally draft-only:

- database_updated: false
- requires_human_confirmation: true

## Tech stack

- Python
- MCP Python SDK / FastMCP
- SQLite
- Faker
- pytest

## Setup

Create and activate a virtual environment:

python -m venv .venv
.\.venv\Scripts\Activate.ps1

Install dependencies:

python -m pip install -r requirements.txt

Seed demo data:

python -m src.bauamt_mcp.seed

Run tests:

pytest tests/test_tools.py

## Run MCP server manually

python -m src.bauamt_mcp.server

The process waits for an MCP client over stdio. If started manually, stop it with Ctrl+C.

## Claude Desktop config

See:

docs/claude_desktop_config.example.json

Use that as a template for your local Claude Desktop MCP configuration.

## Demo record

The seed data always includes this known record:

- Permit ID: BG-2024-0847
- Applicant: Müller Bau GmbH
- Address: Hauptstraße 12, Leipzig
- Status: unterlagen_fehlen
- Missing documents:
  - Brandschutznachweis
  - Statiknachweis

## Interview positioning

This is not just a chatbot. It is a thin MCP layer over a domain system.

The point is that an existing Fachverfahren can become agent-accessible without rebuilding the whole UI first.