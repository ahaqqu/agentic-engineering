-- 0002_remove_fk.sql — Drop FK constraint by recreating items table
-- The users table is not needed; auth is session-based.
DROP TABLE IF EXISTS items;
CREATE TABLE IF NOT EXISTS items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  title TEXT NOT NULL CHECK(length(title) <= 200),
  done INTEGER NOT NULL DEFAULT 0,
  archived INTEGER NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL DEFAULT (unixepoch())
);
CREATE INDEX IF NOT EXISTS idx_items_user ON items(user_id);
