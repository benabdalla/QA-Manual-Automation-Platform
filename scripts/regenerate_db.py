"""
Database Regeneration Script
Run this to recreate the webui_db database with all tables.
"""

import mysql.connector
import os

# Database configuration - update these values
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Add your MySQL password here
    'charset': 'utf8mb4'
}

def regenerate_database():
    """Drop and recreate the database with all tables."""
    
    print("🔄 Starting database regeneration...")
    
    # Connect without specifying database
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Drop old databases
        print("🗑️  Dropping old databases...")
        cursor.execute("DROP DATABASE IF EXISTS webui_auth")
        cursor.execute("DROP DATABASE IF EXISTS webui_db")
        
        # Create new database
        print("📦 Creating webui_db database...")
        cursor.execute("CREATE DATABASE webui_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute("USE webui_db")
        
        # Create users table
        print("📋 Creating users table...")
        cursor.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                last_login TIMESTAMP NULL
            )
        """)
        
        # Create sessions table
        print("📋 Creating sessions table...")
        cursor.execute("""
            CREATE TABLE sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                token_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_valid BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create user_configurations table
        print("📋 Creating user_configurations table...")
        cursor.execute("""
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
            )
        """)
        
        # Create agent_settings table WITH name column
        print("📋 Creating agent_settings table...")
        cursor.execute("""
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
                mcp_json_config TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_agent_setting (user_id, setting_name)
            )
        """)
        
        # Create jira_xray_settings table
        print("📋 Creating jira_xray_settings table...")
        cursor.execute("""
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
            )
        """)
        
        # Create indexes
        print("🔧 Creating indexes...")
        cursor.execute("CREATE INDEX idx_sessions_token_hash ON sessions(token_hash)")
        cursor.execute("CREATE INDEX idx_sessions_user_id ON sessions(user_id)")
        cursor.execute("CREATE INDEX idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX idx_agent_settings_user_id ON agent_settings(user_id)")
        cursor.execute("CREATE INDEX idx_jira_xray_user_id ON jira_xray_settings(user_id)")
        
        conn.commit()
        
        # Verify tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\n✅ Database regenerated successfully!")
        print("📋 Tables created:")
        for table in tables:
            print(f"   - {table[0]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    regenerate_database()
