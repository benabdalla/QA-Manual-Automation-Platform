-- SQL Setup Script for Ines QA Platform
-- Run this in phpMyAdmin or MySQL command line
-- This is the SINGLE consolidated database for the entire project

-- Create database
CREATE DATABASE IF NOT EXISTS webui_db;
USE webui_db;

-- ============================================
-- TABLE: users
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL
);

-- ============================================
-- TABLE: sessions
-- ============================================
CREATE TABLE IF NOT EXISTS sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_valid BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- TABLE: user_configurations
-- ============================================
CREATE TABLE IF NOT EXISTS user_configurations (
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

-- ============================================
-- TABLE: agent_settings (with name column for dropdown)
-- ============================================
CREATE TABLE IF NOT EXISTS agent_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL COMMENT 'Agent display name for dropdown',
    setting_name VARCHAR(100) NOT NULL,
    description VARCHAR(255) DEFAULT '',
    
    -- Agent Type
    agent_type VARCHAR(50) DEFAULT 'org',
    
    -- LLM Settings
    llm_provider VARCHAR(50) DEFAULT 'openai',
    llm_model_name VARCHAR(100) DEFAULT 'gpt-4o',
    llm_temperature FLOAT DEFAULT 1.0,
    llm_base_url VARCHAR(255) DEFAULT '',
    llm_api_key VARCHAR(255) DEFAULT '',
    
    -- Browser LLM Settings
    use_own_browser BOOLEAN DEFAULT FALSE,
    keep_browser_open BOOLEAN DEFAULT FALSE,
    headless BOOLEAN DEFAULT FALSE,
    disable_security BOOLEAN DEFAULT TRUE,
    window_w INT DEFAULT 1280,
    window_h INT DEFAULT 1100,
    save_recording_path VARCHAR(255) DEFAULT './tmp/record_videos',
    save_trace_path VARCHAR(255) DEFAULT './tmp/traces',
    save_agent_history_path VARCHAR(255) DEFAULT './tmp/agent_history',
    
    -- Agent Settings
    use_vision BOOLEAN DEFAULT TRUE,
    max_steps INT DEFAULT 100,
    max_actions_per_step INT DEFAULT 10,
    tool_calling_method VARCHAR(50) DEFAULT 'auto',
    
    -- MCP Settings
    mcp_json_config TEXT DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_agent_setting (user_id, setting_name)
);

-- ============================================
-- TABLE: jira_xray_settings
-- ============================================
CREATE TABLE IF NOT EXISTS jira_xray_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    
    -- Jira Configuration
    jira_requirement_key VARCHAR(255) NOT NULL COMMENT 'Jira requirement key',
    jira_username VARCHAR(255) NOT NULL COMMENT 'Jira username/email',
    jira_url VARCHAR(500) NOT NULL COMMENT 'Jira instance URL',
    jira_api_token LONGTEXT COMMENT 'Jira API token (encrypted)',
    
    -- Project Information
    project_key VARCHAR(100) NOT NULL COMMENT 'Jira project key',
    version_name VARCHAR(255) NOT NULL COMMENT 'Project version name',
    
    -- Xray Configuration
    xray_folder_path VARCHAR(500) NOT NULL COMMENT 'Xray folder path',
    xray_client_id VARCHAR(500) COMMENT 'Xray client ID',
    xray_client_secret LONGTEXT COMMENT 'Xray client secret',
    
    -- Generation Settings
    num_test_cases INT DEFAULT 1 COMMENT 'Number of test cases to generate',
    
    -- Metadata
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX idx_sessions_token_hash ON sessions(token_hash);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_user_configs_user_id ON user_configurations(user_id);
CREATE INDEX idx_user_configs_name ON user_configurations(config_name);
CREATE INDEX idx_agent_settings_user_id ON agent_settings(user_id);
CREATE INDEX idx_agent_settings_name ON agent_settings(setting_name);
CREATE INDEX idx_jira_xray_user_id ON jira_xray_settings(user_id);
CREATE INDEX idx_jira_xray_active ON jira_xray_settings(is_active);
