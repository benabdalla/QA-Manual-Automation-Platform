import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='webui_db'
    )
    cursor = conn.cursor(dictionary=True)
    
    # Check existing agents
    cursor.execute('SELECT * FROM agent_settings WHERE user_id = 1')
    agents = cursor.fetchall()
    print(f'Total agents for user 1: {len(agents)}')
    for agent in agents:
        print(f'  - ID: {agent["id"]}, Name: {agent["setting_name"]}, Model: {agent["llm_model_name"]}')
    
    # If no agents, create test agents
    if len(agents) == 0:
        print('\nCreating test agents...')
        
        test_agents = [
            ('OpenAI GPT-4', 'openai', 'gpt-4', 'sk-your-openai-key-here', 0.7),
            ('Google Gemini', 'google', 'gemini-pro', 'your-gemini-key-here', 0.7),
            ('Claude 3', 'anthropic', 'claude-3-opus-20240229', 'sk-ant-your-key-here', 0.7),
        ]
        
        for name, provider, model, api_key, temp in test_agents:
            cursor.execute("""
                INSERT INTO agent_settings 
                (user_id, setting_name, llm_provider, llm_model_name, llm_temperature, llm_api_key, llm_base_url, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (1, name, provider, model, temp, api_key, '', f'Test agent - {name}'))
        
        conn.commit()
        print(f'Created {len(test_agents)} test agents!')
        
        # Show created agents
        cursor.execute('SELECT * FROM agent_settings WHERE user_id = 1')
        agents = cursor.fetchall()
        print(f'\nNew agents:')
        for agent in agents:
            print(f'  - ID: {agent["id"]}, Name: {agent["setting_name"]}, Model: {agent["llm_model_name"]}')
    
    cursor.close()
    conn.close()
    print('\nDone!')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
