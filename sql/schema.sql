CREATE TABLE IF NOT EXISTS permits (
    id TEXT PRIMARY KEY,
    applicant_name TEXT NOT NULL,
    address TEXT NOT NULL,
    permit_type TEXT NOT NULL CHECK (
        permit_type IN (
            'Neubau',
            'Umbau',
            'Abriss',
            'Nutzungsänderung',
            'Dachausbau',
            'Anbau'
        )
    ),
    status TEXT NOT NULL CHECK (
        status IN (
            'eingereicht',
            'in_prüfung',
            'unterlagen_fehlen',
            'genehmigungsbereit',
            'genehmigt',
            'abgelehnt',
            'überfällig'
        )
    ),
    submitted_date TEXT NOT NULL,
    deadline TEXT NOT NULL,
    missing_documents TEXT NOT NULL DEFAULT '[]',
    assigned_clerk TEXT NOT NULL,
    office_id TEXT NOT NULL,
    estimated_cost_eur REAL,
    last_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_permits_applicant_name
    ON permits (applicant_name);

CREATE INDEX IF NOT EXISTS idx_permits_address
    ON permits (address);

CREATE INDEX IF NOT EXISTS idx_permits_status
    ON permits (status);

CREATE INDEX IF NOT EXISTS idx_permits_submitted_date
    ON permits (submitted_date);

CREATE INDEX IF NOT EXISTS idx_permits_deadline
    ON permits (deadline);

CREATE INDEX IF NOT EXISTS idx_permits_office_id
    ON permits (office_id);