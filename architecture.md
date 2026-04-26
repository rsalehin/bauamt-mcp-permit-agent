# Architecture — Bauamt MCP Permit Agent

## Purpose

This project demonstrates how a legacy-style municipal permit system can be exposed to an AI assistant through a narrow MCP layer.

The goal is not to build a full Bauamt web application. The goal is to show the integration pattern:

Claude Desktop
→ MCP server
→ domain tools
→ permit database
→ structured answer

## System overview

Claude Desktop acts as the MCP host.

The Python MCP server exposes four domain-specific tools:

- search_permits
- get_permit_details
- get_kpi_summary
- prepare_data_entry

The tools query a local SQLite database seeded with 50 fake German building-permit records.

## Runtime flow

1. A clerk asks Claude a German natural-language question.
2. Claude decides whether one of the MCP tools is useful.
3. Claude calls the MCP tool with structured arguments.
4. The Python server validates the tool call through typed function signatures.
5. The tool queries the SQLite permit database.
6. The tool returns structured data.
7. Claude explains the result in natural language.

## Data layer

The demo uses SQLite for portability.

In a production system, this layer could be replaced by:

- PostgreSQL
- Oracle
- Microsoft SQL Server
- an existing Fachverfahren database
- an internal HTTP API

The important design point is that the MCP tool layer hides raw database access from Claude.

## Tool boundary

Claude does not receive arbitrary SQL access.

Instead, Claude only gets narrow domain operations:

### search_permits

Read-only search over permits.

### get_permit_details

Read-only detail retrieval for one permit.

### get_kpi_summary

Read-only reporting/KPI calculation.

### prepare_data_entry

Draft-only write preparation.

This tool does not write to the database. It returns a structured draft that a human clerk must review.

## Safety model

The server follows three safety rules:

1. No arbitrary SQL tool.
2. No direct write operation from Claude.
3. Write-like actions return draft payloads only.

The response from prepare_data_entry always includes:

- database_updated: false
- requires_human_confirmation: true

## Why MCP here?

An ordinary API is still mainly a developer-facing integration surface.

An MCP server makes selected system capabilities directly usable by an MCP-capable AI client. Claude can discover and call the exposed tools during a conversation.

This is useful for legacy business systems because the first modernization step does not need to be a full UI rewrite. A thin MCP adapter can make selected workflows agent-accessible.

## Current limitations

This is a portfolio demo, not a production system.

Production hardening would require:

- authentication
- authorization
- audit logging
- structured observability
- deployment configuration
- real database integration
- stricter input validation
- approval workflow UI
- rate limiting
- permission-aware tool exposure

## Interview takeaway

The architectural pattern is:

Existing Fachverfahren
→ narrow safe tool layer
→ MCP server
→ AI assistant
→ faster clerk workflow

The system becomes agent-accessible without giving the AI unrestricted access to the underlying database.