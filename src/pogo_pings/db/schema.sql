CREATE TABLE IF NOT EXISTS seen_codes (
    code TEXT PRIMARY KEY,
    rewards TEXT NOT NULL,
    source TEXT NOT NULL,
    notified_at TEXT
);
