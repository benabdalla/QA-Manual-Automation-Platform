-- ============================================
-- REGENERATE DATABASE SCRIPT
-- WARNING: This will DELETE all existing data!
-- Backup your data first!
-- ============================================

-- Step 1: Drop old databases
DROP DATABASE IF EXISTS webui_auth;
DROP DATABASE IF EXISTS webui_db;

-- Step 2: Create fresh database
CREATE DATABASE webui_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE webui_db;

-- Step 3: Create all tables
-- (Copy all CREATE TABLE statements from setup.sql)

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL
);

-- Sessions table
CREATE TABLE sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_valid BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- User configurations table
CREATE TABLE user_configurations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    config_name VARCHAR(100) NOT NULL,
    config_data LONGTEXT NOT NULL,
    description VARCHAR(255) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_config (user_id, config_name)
);

-- Agent settings table (WITH name column)
CREATE TABLE agent_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL COMMENT 'Agent display name',
    setting_name VARCHAR(100) NOT NULL,
    description VARCHAR(255) DEFAULT '',
    agent_type VARCHAR(50) DEFAULT 'org',
    llm_provider VARCHAR(50) DEFAULT 'openai',
    llm_model_name VARCHAR(100) DEFAULT 'gpt-4o',
    llm_temperature FLOAT DEFAULT 1.0,
    llm_base_url VARCHAR(255) DEFAULT '',
    llm_api_key VARCHAR(255) DEFAULT '',
    use_own_browser BOOLEAN DEFAULT FALSE,
    keep_browser_open BOOLEAN DEFAULT FALSE,
    headless BOOLEAN DEFAULT FALSE,
    disable_security BOOLEAN DEFAULT TRUE,
    window_w INT DEFAULT 1280,
    window_h INT DEFAULT 1100,
    save_recording_path VARCHAR(255) DEFAULT './tmp/record_videos',
    save_trace_path VARCHAR(255) DEFAULT './tmp/traces',
    save_agent_history_path VARCHAR(255) DEFAULT './tmp/agent_history',
    use_vision BOOLEAN DEFAULT TRUE,
    max_steps INT DEFAULT 100,
    max_actions_per_step INT DEFAULT 10,
    tool_calling_method VARCHAR(50) DEFAULT 'auto',
    mcp_json_config TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_agent_setting (user_id, setting_name)
);

-- Jira Xray settings table
CREATE TABLE jira_xray_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    jira_requirement_key VARCHAR(255) NOT NULL,
    jira_username VARCHAR(255) NOT NULL,
    jira_url VARCHAR(500) NOT NULL,
    jira_api_token LONGTEXT,
    project_key VARCHAR(100) NOT NULL,
    version_name VARCHAR(255) NOT NULL,
    xray_folder_path VARCHAR(500) NOT NULL,
    xray_client_id VARCHAR(500),
    xray_client_secret LONGTEXT,
    num_test_cases INT DEFAULT 1,
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX idx_sessions_token_hash ON sessions(token_hash);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_agent_settings_user_id ON agent_settings(user_id);
CREATE INDEX idx_jira_xray_user_id ON jira_xray_settings(user_id);

-- Step 4: Create default admin user (password: Admin123!)
-- Generate hash using: python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('Admin123!'))"
INSERT INTO users (username, email, password_hash) VALUES 
('admin', 'admin@example.com', 'scrypt:32768:8:1$YOUR_HASH_HERE');

-- Verify tables created
SHOW TABLES;
SELECT 'Database regenerated successfully!' AS status;
