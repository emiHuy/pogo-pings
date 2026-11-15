CREATE TABLE IF NOT EXISTS seen_codes (
    code TEXT PRIMARY KEY,
    reward ARRAY,
    source TEXT,
    discovered_at TEXT NOT NULL,
    notified_at TEXT
);
