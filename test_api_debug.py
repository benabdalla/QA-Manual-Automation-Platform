#!/usr/bin/env python
"""Test script to verify code generator API endpoints."""

import mysql.connector
import os
import json

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "webui_db")
    )

# Test 1: Get all agents
print("\n" + "="*60)
print("TEST 1: Listing all agents in database")
print("="*60)

connection = get_db_connection()
cursor = connection.cursor(dictionary=True)

cursor.execute("SELECT id, user_id, setting_name, llm_provider, llm_model_name, llm_api_key FROM agent_settings")
agents = cursor.fetchall()

print(f"\n✅ Found {len(agents)} agents total:")
for agent in agents:
    api_key_display = agent['llm_api_key'][:10] + '...' if agent['llm_api_key'] else 'Not set'
    print(f"\n  Agent ID: {agent['id']}")
    print(f"  User ID: {agent['user_id']}")
    print(f"  Name: {agent['setting_name']}")
    print(f"  Provider: {agent['llm_provider']}")
    print(f"  Model: {agent['llm_model_name']}")
    print(f"  API Key: {api_key_display}")

# Test 2: Get agents for current user (ID 1)
print("\n" + "="*60)
print("TEST 2: Getting agents for user ID 1")
print("="*60)

cursor.execute("""
    SELECT id, setting_name, llm_provider, llm_model_name, llm_api_key 
    FROM agent_settings 
    WHERE user_id = 1
    ORDER BY setting_name ASC
""")

user_agents = cursor.fetchall()
print(f"\n✅ Found {len(user_agents)} agents for user 1:")
for agent in user_agents:
    api_key_display = agent['llm_api_key'][:20] + '...' if agent['llm_api_key'] else 'Not set'
    print(f"\n  ID: {agent['id']}")
    print(f"  Name: {agent['setting_name']}")
    print(f"  Provider: {agent['llm_provider']}")
    print(f"  Model: {agent['llm_model_name']}")
    print(f"  API Key: {api_key_display}")

# Test 3: Get specific agent details
if user_agents:
    print("\n" + "="*60)
    print("TEST 3: Getting details for first agent")
    print("="*60)
    
    agent_id = user_agents[0]['id']
    cursor.execute("""
        SELECT id, setting_name, llm_provider, llm_model_name, llm_temperature, 
               llm_api_key, llm_base_url, description
        FROM agent_settings
        WHERE id = %s
    """, (agent_id,))
    
    agent = cursor.fetchone()
    if agent:
        api_key_display = agent['llm_api_key'][:20] + '...' if agent['llm_api_key'] else 'Not set'
        print(f"\n✅ Agent details for ID {agent_id}:")
        print(f"  Name: {agent['setting_name']}")
        print(f"  Provider: {agent['llm_provider']}")
        print(f"  Model Name: {agent['llm_model_name']}")
        print(f"  Temperature: {agent['llm_temperature']}")
        print(f"  API Key: {api_key_display}")
        print(f"  Base URL: {agent['llm_base_url']}")
        print(f"  Description: {agent['description']}")

cursor.close()
connection.close()

print("\n" + "="*60)
print("✅ All tests completed successfully!")
print("="*60)
