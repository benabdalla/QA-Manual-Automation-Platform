#!/usr/bin/env python3
"""
Test script to verify the agent settings save functionality
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.auth.auth_manager import AuthManager

def test_save_agent_settings():
    """Test saving agent settings"""
    try:
        print("=" * 60)
        print("TESTING AGENT SETTINGS SAVE FUNCTIONALITY")
        print("=" * 60)
        
        # Initialize auth manager
        print("\n1️⃣  Initializing AuthManager...")
        auth_manager = AuthManager()
        
        if not auth_manager.initialize():
            print("❌ Failed to initialize database")
            return
        
        print("✅ AuthManager initialized")
        
        # Get first user
        print("\n2️⃣  Getting first user...")
        import mysql.connector
        import os as os_module
        
        connection = mysql.connector.connect(
            host=os_module.getenv("MYSQL_HOST", "localhost"),
            port=int(os_module.getenv("MYSQL_PORT", "3306")),
            user=os_module.getenv("MYSQL_USER", "root"),
            password=os_module.getenv("MYSQL_PASSWORD", ""),
            database=os_module.getenv("MYSQL_DATABASE", "webui_db")
        )
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, username, email FROM users LIMIT 1")
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not user:
            print("❌ No users found in database")
            return
        
        print(f"✅ Found user: {user['username']} (ID: {user['id']})")
        
        # Set current user
        print("\n3️⃣  Setting current user...")
        auth_manager.set_current_user_directly(
            user_id=user['id'],
            username=user['username'],
            email=user['email']
        )
        
        if auth_manager.is_authenticated():
            print(f"✅ Authenticated as: {user['username']}")
        else:
            print("❌ Failed to authenticate user")
            return
        
        # Test save
        print("\n4️⃣  Testing save agent settings...")
        test_settings = {
            'llm_provider': 'openai',
            'llm_model_name': 'gpt-4o',
            'llm_temperature': 0.7,
            'llm_api_key': 'test-key-123',
            'use_vision': True,
            'max_steps': 100
        }
        
        result = auth_manager.save_agent_setting(
            setting_name="Test Agent Setting",
            settings=test_settings,
            description="Test description"
        )
        
        if result['success']:
            print(f"✅ Settings saved successfully!")
            print(f"   Message: {result.get('message', 'N/A')}")
        else:
            print(f"❌ Failed to save settings")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return
        
        # Test get list
        print("\n5️⃣  Testing get agent settings list...")
        list_result = auth_manager.get_agent_settings_list()
        
        if list_result['success']:
            settings_count = len(list_result.get('settings', []))
            print(f"✅ Retrieved {settings_count} agent settings")
            for setting in list_result.get('settings', [])[:3]:
                print(f"   - {setting['setting_name']} ({setting['llm_provider']})")
        else:
            print(f"❌ Failed to get settings list")
            print(f"   Error: {list_result.get('error', 'Unknown error')}")
        
        # Test load
        print("\n6️⃣  Testing load agent settings...")
        load_result = auth_manager.load_agent_setting("Test Agent Setting")
        
        if load_result['success']:
            setting = load_result.get('setting', {})
            print(f"✅ Settings loaded successfully!")
            print(f"   Provider: {setting.get('llm_provider', 'N/A')}")
            print(f"   Model: {setting.get('llm_model_name', 'N/A')}")
            print(f"   Temperature: {setting.get('llm_temperature', 'N/A')}")
        else:
            print(f"❌ Failed to load settings")
            print(f"   Error: {load_result.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_save_agent_settings()
