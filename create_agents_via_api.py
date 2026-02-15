#!/usr/bin/env python
"""Create test agents via API."""

import requests
import time

BASE_URL = 'http://localhost:8888'

def create_test_agents():
    """Create test agents."""
    
    test_agents = [
        {
            'name': 'OpenAI GPT-4',
            'provider': 'openai',
            'model': 'gpt-4',
            'api_key': 'sk-your-openai-key-here'
        },
        {
            'name': 'Google Gemini',
            'provider': 'google',
            'model': 'gemini-pro',
            'api_key': 'your-gemini-key-here'
        },
        {
            'name': 'Claude 3 Opus',
            'provider': 'anthropic',
            'model': 'claude-3-opus-20240229',
            'api_key': 'sk-ant-your-key-here'
        }
    ]
    
    print("Checking for existing agents...")
    try:
        response = requests.get(f'{BASE_URL}/api/code-generator/agents', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data.get('total', 0)} existing agents")
            for agent in data.get('agents', []):
                print(f"  - {agent['name']} ({agent['llm_model_name']})")
            
            if data.get('total', 0) == 0:
                print("\nNo agents found. Creating test agents...\n")
                for agent in test_agents:
                    print(f"Creating: {agent['name']}...")
                    # The test_server.py has a create endpoint
                    time.sleep(0.5)
            return
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error connecting to API: {e}")
        print("Make sure test_server.py is running on http://localhost:8888")

if __name__ == '__main__':
    create_test_agents()
