-- Jira-Xray Settings Table
-- This script creates the jira_xray_settings table in the webui_db database

CREATE TABLE IF NOT EXISTS `jira_xray_settings` (
  `id` int NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_id` int NOT NULL,
  
  -- Jira Configuration
  `jira_requirement_key` varchar(255) NOT NULL COMMENT 'Jira requirement key (e.g., W250-6073)',
  `jira_username` varchar(255) NOT NULL COMMENT 'Jira username/email',
  `jira_url` varchar(500) NOT NULL COMMENT 'Jira instance URL',
  `jira_api_token` longtext COMMENT 'Jira API token (encrypted)',
  
  -- Project Information
  `project_key` varchar(100) NOT NULL COMMENT 'Jira project key (e.g., Dev)',
  `version_name` varchar(255) NOT NULL COMMENT 'Project version name (e.g., v1)',
  
  -- Xray Configuration
  `xray_folder_path` varchar(500) NOT NULL COMMENT 'Xray folder path',
  `xray_client_id` varchar(500) COMMENT 'Xray client ID (encrypted)',
  `xray_client_secret` longtext COMMENT 'Xray client secret (encrypted)',
  
  -- Generation Settings
  `num_test_cases` int DEFAULT 1 COMMENT 'Number of test cases to generate (1-100)',
  
  -- Metadata
  `is_active` tinyint(1) DEFAULT 1 COMMENT 'Is this configuration active',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  -- Constraints
  CONSTRAINT `fk_jira_xray_settings_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  KEY `idx_user_id` (`user_id`),
  KEY `idx_project_key` (`project_key`),
  KEY `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Jira-Xray configuration settings per user';

-- Create index for faster lookups
ALTER TABLE `jira_xray_settings` ADD INDEX `idx_user_id_active` (`user_id`, `is_active`);
