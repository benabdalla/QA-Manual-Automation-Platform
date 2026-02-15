-- Migration: Add 'name' column to agent_settings table
-- Run this if your agent_settings table doesn't have a 'name' column

USE webui_db;

-- Check if column exists, if not add it
SET @column_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = 'webui_db' 
    AND TABLE_NAME = 'agent_settings' 
    AND COLUMN_NAME = 'name'
);

-- Add the column if it doesn't exist
ALTER TABLE agent_settings 
ADD COLUMN IF NOT EXISTS name VARCHAR(100) NOT NULL DEFAULT '' AFTER user_id;

-- Copy setting_name to name where name is empty
UPDATE agent_settings SET name = setting_name WHERE name = '' OR name IS NULL;

-- Verify the update
SELECT id, name, setting_name, llm_model_name, llm_provider FROM agent_settings;
