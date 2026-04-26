from __future__ import annotations

import json
import random
from datetime import date, datetime, timedelta

from faker import Faker

from src.bauamt_mcp.db import get_connection, initialize_database


fake = Faker("de_DE")
Faker.seed(42)
random.seed(42)


PERMIT_TYPES = [
    "Neubau",
    "Umbau",
    "Abriss",
    "Nutzungsänderung",
    "Dachausbau",
    "Anbau",
]

STATUSES = [
    "eingereicht",
    "in_prüfung",
    "unterlagen_fehlen",
    "genehmigungsbereit",
    "genehmigt",
    "abgelehnt",
    "überfällig",
]

DOCUMENTS = [
    "Lageplan",
    "Bauantragsformular",
    "Baubeschreibung",
    "Brandschutznachweis",
    "Statiknachweis",
    "Entwässerungsplan",
    "Energieausweis",
    "Nachweis Stellplätze",
    "Eigentumsnachweis",
    "Schallschutznachweis",
]

CLERKS = [
    "Frau Schneider",
    "Herr Müller",
    "Frau Wagner",
    "Herr Becker",
    "Frau Hoffmann",
]

OFFICES = [
    "BAUAMT-LE-01",
    "BAUAMT-LE-02",
    "BAUAMT-LE-03",
]

STREETS = [
    "Hauptstraße",
    "Bahnhofstraße",
    "Leipziger Straße",
    "Schillerstraße",
    "Goethestraße",
    "Gartenstraße",
    "Dorfstraße",
    "Karl-Liebknecht-Straße",
    "August-Bebel-Straße",
    "Markt",
]


def random_address() -> str:
    street = random.choice(STREETS)
    house_number = random.randint(1, 120)
    city = random.choice(["Leipzig", "Markranstädt", "Borna", "Grimma", "Taucha"])
    return f"{street} {house_number}, {city}"


def random_missing_documents(status: str) -> list[str]:
    if status == "unterlagen_fehlen":
        return random.sample(DOCUMENTS, random.randint(1, 4))

    if status in {"eingereicht", "in_prüfung"} and random.random() < 0.3:
        return random.sample(DOCUMENTS, random.randint(1, 2))

    return []


def derive_status(submitted_date: date, deadline: date) -> str:
    today = date.today()

    if deadline < today - timedelta(days=30):
        return "überfällig"

    if deadline < today:
        return random.choice(["überfällig", "in_prüfung", "unterlagen_fehlen"])

    return random.choice(STATUSES[:-1])


def build_permit(index: int) -> tuple:
    year = random.choice([2024, 2025, 2026])
    submitted = date(year, random.randint(1, 12), random.randint(1, 28))
    deadline = submitted + timedelta(days=random.choice([45, 60, 90, 120]))

    status = derive_status(submitted, deadline)
    missing_docs = random_missing_documents(status)

    # Ensure a known demo record exists.
    if index == 1:
        permit_id = "BG-2024-0847"
        applicant_name = "Müller Bau GmbH"
        address = "Hauptstraße 12, Leipzig"
        permit_type = "Umbau"
        status = "unterlagen_fehlen"
        submitted = date(2024, 8, 12)
        deadline = date(2024, 11, 12)
        missing_docs = ["Brandschutznachweis", "Statiknachweis"]
        assigned_clerk = "Frau Schneider"
        office_id = "BAUAMT-LE-01"
        estimated_cost = 248000.00
    else:
        permit_id = f"BG-{year}-{index:04d}"
        applicant_name = random.choice(
            [
                fake.name(),
                f"{fake.last_name()} Bau GmbH",
                f"{fake.last_name()} Immobilien GmbH",
                f"{fake.last_name()} Projektentwicklung",
            ]
        )
        address = random_address()
        permit_type = random.choice(PERMIT_TYPES)
        assigned_clerk = random.choice(CLERKS)
        office_id = random.choice(OFFICES)
        estimated_cost = round(random.uniform(15000, 950000), 2)

    return (
        permit_id,
        applicant_name,
        address,
        permit_type,
        status,
        submitted.isoformat(),
        deadline.isoformat(),
        json.dumps(missing_docs, ensure_ascii=False),
        assigned_clerk,
        office_id,
        estimated_cost,
        datetime.now().isoformat(timespec="seconds"),
    )


def seed_database(count: int = 50) -> None:
    initialize_database()

    permits = [build_permit(index) for index in range(1, count + 1)]

    with get_connection() as conn:
        conn.execute("DELETE FROM permits")
        conn.executemany(
            """
            INSERT INTO permits (
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
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            permits,
        )
        conn.commit()

    print(f"Seeded {len(permits)} fake Bauamt permits.")


if __name__ == "__main__":
    seed_database()