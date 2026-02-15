#!/bin/bash
# Quick Test Script for Flask Agent Integration

echo "🚀 Flask Agent Integration - Quick Test Guide"
echo "=============================================="
echo ""

# Test 1: Health Check
echo "📋 Test 1: Health Check"
echo "Command:"
echo 'curl -X GET "http://127.0.0.1:5000/api/health"'
echo ""
echo "Expected: 200 OK"
echo "Response should show: {\"success\": true}"
echo ""

# Test 2: Get User Configs
echo "📋 Test 2: Get Saved Configurations"
echo "Command:"
echo 'curl -X GET "http://127.0.0.1:5000/api/configs" -H "Cookie: session=YOUR_SESSION_ID"'
echo ""
echo "Expected: 200 OK"
echo "Response should show: {\"success\": true, \"configs\": [...]}"
echo ""

# Test 3: Run Agent (main test)
echo "📋 Test 3: Run Browser Use Agent (MAIN TEST)"
echo "Command:"
echo 'curl -X POST "http://127.0.0.1:5000/api/run-agent" \'
echo '  -H "Content-Type: application/json" \'
echo '  -H "Cookie: session=YOUR_SESSION_ID" \'
echo '  -d "{"
echo '    \"agent_type\": \"browser_use\",'
echo '    \"task\": \"Navigate to google.com\",'
echo '    \"provider\": \"openai\",'
echo '    \"model\": \"gpt-4\",'
echo '    \"api_key\": \"sk-YOUR-API-KEY\"'
echo '  }"'
echo ""
echo "Expected: 200 OK"
echo "Response should show:"
echo '{'
echo '  "success": true,'
echo '  "agent_id": "uuid-here",'
echo '  "data": {'
echo '    "status": "completed",'
echo '    "duration": 15.3,'
echo '    "result": {...}'
echo '  }'
echo '}'
echo ""

# Test 4: Get Agent Status
echo "📋 Test 4: Get Agent Status"
echo "Command:"
echo 'curl -X GET "http://127.0.0.1:5000/api/agent-status/AGENT_UUID_FROM_TEST_3"'
echo ""
echo "Expected: 200 OK"
echo "Response should show: {\"success\": true, \"data\": {...}}"
echo ""

# Test 5: Get Agent History
echo "📋 Test 5: Get Execution History"
echo "Command:"
echo 'curl -X GET "http://127.0.0.1:5000/api/agent-history?limit=10" \'
echo '  -H "Cookie: session=YOUR_SESSION_ID"'
echo ""
echo "Expected: 200 OK"
echo "Response should show: {\"success\": true, \"data\": [...]}"
echo ""

# Test 6: Through Web UI
echo "📋 Test 6: Test Through Web UI (EASIEST)"
echo "Steps:"
echo "1. Open http://127.0.0.1:5000 in browser"
echo "2. Login with admin / Admin123"
echo "3. Click 'Test IA Agent' card on home page"
echo "4. Fill form:"
echo "   - Agent Type: Browser Use Agent"
echo "   - Task: 'Navigate to google.com'"
echo "   - Provider: openai"
echo "   - Model: gpt-4"
echo "5. Click 'Launch Agent'"
echo "6. Watch status panel for results"
echo ""

echo "=================================================="
echo "🔑 Important Notes:"
echo "=================================================="
echo ""
echo "1. You need to have an API key for OpenAI or Ollama"
echo "2. For first time, save your API key in settings"
echo "3. Agent execution takes time (30 seconds to 5 minutes)"
echo "4. Check Flask console for detailed logs"
echo "5. Results are saved to database automatically"
echo ""

echo "🚨 Common Issues:"
echo ""
echo "❌ ModuleNotFoundError: Make sure requirements installed"
echo "   Solution: pip install -r requirements_flask.txt"
echo ""
echo "❌ API key not found: Add key in dashboard settings"
echo "   Solution: Go to Settings → Add API Key"
echo ""
echo "❌ Agent timeout: Agent took too long"
echo "   Solution: Use simpler tasks, increase timeout in settings"
echo ""
echo "❌ LLM error: Provider/model not available"
echo "   Solution: Check if API key is valid and provider is online"
echo ""

echo "✅ All Tests Ready!"
echo "Start Flask and try the tests above."
echo ""
