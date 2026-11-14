CREATE TABLE IF NOT EXISTS seen_codes (
    code TEXT PRIMARY KEY,
    source TEXT,
    discovered_at TEXT NOT NULL,
    notified_at TEXT
);
