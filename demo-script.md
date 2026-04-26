# Demo Script — Bauamt MCP Permit Agent

## One-sentence pitch

This demo shows how a legacy-style German Bauamt permit system can be exposed as an MCP server so Claude can search permits, inspect missing documents, calculate office KPIs, and prepare draft-only data entries from natural German instructions.

## Core interview thesis

Das Fachsystem war bisher nur über seine eigene Oberfläche nutzbar. Als MCP-Server kann Claude die relevanten Fachfunktionen direkt verwenden: Bauanträge suchen, fehlende Unterlagen anzeigen, KPIs berechnen und Dateneingaben vorbereiten. Der Sachbearbeiter muss dafür nicht mehr manuell durch das System navigieren, und kritische Änderungen bleiben trotzdem prüfpflichtig.

## What the demo proves

- MCP tool integration over a domain system
- German natural-language workflow
- Structured permit search
- Detail retrieval
- KPI calculation
- Safe draft-only write preparation
- No arbitrary SQL exposure
- Human approval boundary for risky actions

## Pre-demo checks

Run before the interview:

pytest tests/test_tools.py

Expected:

6 passed

## Demo prompt 1 — Search permits

Ask Claude:

Finde alle Bauanträge für Hauptstraße 12 aus dem Jahr 2024.

Expected MCP tool:

search_permits

Expected visible result:

- Permit ID: BG-2024-0847
- Applicant: Müller Bau GmbH
- Address: Hauptstraße 12, Leipzig
- Status: unterlagen_fehlen
- Assigned clerk: Frau Schneider

Suggested explanation:

Hier sieht man den ersten Nutzen: Der Sachbearbeiter muss nicht manuell im Fachsystem suchen. Claude ruft gezielt das MCP-Tool search_permits auf und bekommt strukturierte Fachdaten zurück.

## Demo prompt 2 — Missing documents

Ask Claude:

Welche Unterlagen fehlen noch für BG-2024-0847?

Expected MCP tool:

get_permit_details

Expected visible result:

- Brandschutznachweis
- Statiknachweis

Suggested explanation:

Claude beantwortet die Frage nicht aus freiem Text oder Halluzination, sondern über ein eng definiertes Fach-Tool. Das ist wichtig, weil die Antwort aus dem Systemzustand kommt.

## Demo prompt 3 — KPI reporting

Ask Claude:

Wie viele Anträge im BAUAMT-LE-01 sind zwischen 2024-01-01 und 2026-12-31 mehr als 30 Tage überfällig?

Expected MCP tool:

get_kpi_summary

Expected visible result includes:

- total_permits
- pending_permits
- overdue_more_than_30_days
- missing_documents_cases
- average_nominal_processing_days

Suggested explanation:

Das ist der Reporting-Teil. Statt manuell Daten aus dem System zu kopieren, kann Claude eine KPI-Abfrage ausführen und die Zahlen direkt strukturiert zurückgeben.

## Demo prompt 4 — Safe draft-only data entry

Ask Claude:

Bereite eine Dateneingabe vor, um BG-2024-0847 als genehmigungsbereit zu markieren. Setze das Freigabedatum auf 2026-04-26 und füge die Notiz hinzu: Alle erforderlichen Unterlagen liegen vor. Nicht speichern.

Expected MCP tool:

prepare_data_entry

Expected safety result:

- database_updated: false
- requires_human_confirmation: true

Suggested explanation:

Das ist bewusst kein echter Schreibzugriff. Claude darf eine Dateneingabe vorbereiten, aber nicht direkt speichern. Damit bleibt der Sachbearbeiter in der Verantwortung, und kritische Änderungen bleiben prüfpflichtig.

## Why MCP instead of only an API?

Eine API wäre weiterhin primär eine Entwickler-Schnittstelle. Ein MCP-Server macht die Fachfunktionen direkt für einen LLM-Client nutzbar. Claude kann die verfügbaren Tools erkennen, gezielt aufrufen und strukturierte Ergebnisse in der Unterhaltung verwenden.

## Safety boundary

Claude bekommt keine freie SQL-Schnittstelle. Es gibt nur fachlich definierte Operationen:

- search_permits
- get_permit_details
- get_kpi_summary
- prepare_data_entry

prepare_data_entry ist absichtlich draft-only. Es schreibt nicht in die Datenbank.

## Closing line for the interview

Das eigentliche Muster ist: Ein bestehendes Fachsystem muss nicht sofort komplett neu gebaut werden. Man kann zuerst eine sichere MCP-Schicht über die wichtigsten Fachfunktionen legen und dadurch das System agentenfähig machen.