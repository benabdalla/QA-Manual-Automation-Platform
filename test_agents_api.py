#!/usr/bin/env python3
"""
Test script to check if agents exist in the database
"""
import os
import sys
import mysql.connector
from mysql.connector import Error

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database():
    """Check database connection and agents"""
    try:
        print("🔍 Checking database connection...")
        
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", "webui_db")
        )
        
        if connection.is_connected():
            print("✅ Connected to database")
            
            cursor = connection.cursor(dictionary=True)
            
            # Check users
            print("\n📋 Checking users...")
            cursor.execute("SELECT id, username FROM users LIMIT 5")
            users = cursor.fetchall()
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"  - ID: {user['id']}, Username: {user['username']}")
            
            # Check agents
            print("\n🤖 Checking agent_settings...")
            cursor.execute("SELECT COUNT(*) as count FROM agent_settings")
            total_agents = cursor.fetchone()['count']
            print(f"Total agents in database: {total_agents}")
            
            if total_agents > 0:
                cursor.execute("""
                    SELECT id, user_id, setting_name, llm_provider, llm_model_name 
                    FROM agent_settings 
                    LIMIT 10
                """)
                agents = cursor.fetchall()
                print(f"\nFound {len(agents)} agents:")
                for agent in agents:
                    print(f"  - ID: {agent['id']}, User: {agent['user_id']}, Name: {agent['setting_name']}, Provider: {agent['llm_provider']}, Model: {agent['llm_model_name']}")
            
            # Get all users with their agents
            print("\n👥 All Users and Their Agents:")
            cursor.execute("SELECT id, username FROM users")
            all_users = cursor.fetchall()
            
            for user in all_users:
                user_id = user['id']
                username = user['username']
                
                cursor.execute("""
                    SELECT id, setting_name, llm_provider, llm_model_name 
                    FROM agent_settings 
                    WHERE user_id = %s
                """, (user_id,))
                
                user_agents = cursor.fetchall()
                agent_count = len(user_agents) if user_agents else 0
                print(f"  👤 {username} (ID: {user_id}): {agent_count} agents")
                
                if user_agents:
                    for agent in user_agents:
                        print(f"     └─ {agent['setting_name']} ({agent['llm_provider']})")
            
            # Get user-specific agents (assuming user 1)
            print("\n🎯 Checking agents for user 1...")
            cursor.execute("""
                SELECT id, setting_name, llm_provider, llm_model_name 
                FROM agent_settings 
                WHERE user_id = 1
            """)
            user_agents = cursor.fetchall()
            print(f"Found {len(user_agents)} agents for user 1:")
            for agent in user_agents:
                print(f"  - ID: {agent['id']}, Name: {agent['setting_name']}, Provider: {agent['llm_provider']}, Model: {agent['llm_model_name']}")
            
            cursor.close()
            connection.close()
            
        else:
            print("❌ Failed to connect to database")
            
    except Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE DIAGNOSTIC TEST")
    print("=" * 60)
    check_database()
    print("\n" + "=" * 60)
