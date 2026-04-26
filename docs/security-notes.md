# Security Notes — Bauamt MCP Permit Agent

## Security posture

This project is a local portfolio demo. It is not a production-ready government software system.

The goal is to demonstrate a safe MCP integration pattern over a domain workflow.

## Main risks

MCP servers expose tools to AI clients. That creates an action surface.

Important risks include:

- excessive tool permissions
- unsafe write operations
- arbitrary SQL access
- prompt/tool injection
- misleading tool descriptions
- accidental exposure of sensitive data
- missing audit logging
- unclear human approval boundaries

## Design decisions in this demo

### No arbitrary SQL

Claude does not receive a generic SQL tool.

Instead, the server exposes only domain-specific tools:

- search_permits
- get_permit_details
- get_kpi_summary
- prepare_data_entry

### Draft-only write preparation

The prepare_data_entry tool intentionally does not write to the database.

It only returns a proposed update.

Expected safety fields:

- database_updated: false
- requires_human_confirmation: true

### Synthetic data only

The database contains fake permit records generated for the demo.

No real citizen, company, or government data is used.

### Narrow tool surface

Each tool maps to one business operation.

The tools do not expose:

- shell execution
- raw file access
- arbitrary database mutation
- unrestricted external API calls

## Production hardening checklist

Before a real deployment, this system would need:

- authentication
- role-based authorization
- permission-aware tool exposure
- audit logging
- approval workflow UI
- input validation
- output validation
- secret management
- monitoring and alerting
- deployment isolation
- rate limiting
- security review of tool descriptions
- tests for prompt injection and tool misuse

## Interview takeaway

The important principle is not "let Claude access everything."

The principle is:

Expose only narrow, auditable, domain-specific operations through MCP, and keep risky actions behind human review.