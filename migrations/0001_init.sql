-- 0001_init.sql — core tables
-- Note: auth is session-cookie-based; no users table needed.
-- The user_id in items corresponds to the session.sub claim.

CREATE TABLE IF NOT EXISTS items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  title TEXT NOT NULL CHECK(length(title) <= 200),
  done INTEGER NOT NULL DEFAULT 0,
  archived INTEGER NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL DEFAULT (unixepoch())
);

CREATE INDEX IF NOT EXISTS idx_items_user ON items(user_id);
