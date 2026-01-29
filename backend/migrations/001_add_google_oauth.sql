-- Migration: Add Google OAuth support
-- Run this on existing database to add google_id column

-- Add google_id column if not exists
ALTER TABLE users ADD COLUMN google_id VARCHAR(255) UNIQUE;

-- Add last_active column if not exists (used in auth)
ALTER TABLE users ADD COLUMN last_active TIMESTAMP;

-- Create index for faster Google ID lookups
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
