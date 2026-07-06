-- 0002_items_archived.sql — Add archived column to existing items table
ALTER TABLE items ADD COLUMN archived INTEGER NOT NULL DEFAULT 0;
