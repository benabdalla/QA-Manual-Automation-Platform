-- ============================================
-- CLEANUP SCRIPT - Remove old webui_auth database
-- WARNING: BACKUP YOUR DATA BEFORE RUNNING THIS!
-- ============================================

-- Step 1: Verify all data is in webui_db
USE webui_db;
SELECT 'Users count:' AS info, COUNT(*) AS count FROM users;
SELECT 'Agent settings count:' AS info, COUNT(*) AS count FROM agent_settings;
SELECT 'Sessions count:' AS info, COUNT(*) AS count FROM sessions;

-- Step 2: Drop the old database (UNCOMMENT TO EXECUTE)
-- DROP DATABASE IF EXISTS webui_auth;

-- Step 3: Verify only webui_db remains
SHOW DATABASES LIKE 'webui%';
