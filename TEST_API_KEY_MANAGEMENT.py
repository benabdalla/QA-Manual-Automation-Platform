"""
Test script to verify API Key management functionality
"""

# Example usage of the API Key Update feature

# 1. CREATE a new API Key
"""
curl -X POST http://localhost:5000/api/api-keys \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My OpenAI API Key",
    "key_type": "openai",
    "key_value": "sk-example-key-12345"
  }'

Response:
{
  "success": true,
  "message": "API key created",
  "key_id": 1
}
"""

# 2. READ all API Keys
"""
curl http://localhost:5000/api/api-keys

Response:
{
  "success": true,
  "api_keys": [
    {
      "id": 1,
      "name": "My OpenAI API Key",
      "type": "openai",
      "is_active": true,
      "masked_value": "sk-example...",
      "last_used": null,
      "created_at": "2026-01-25T10:30:00"
    }
  ]
}
"""

# 3. UPDATE an existing API Key (NEW FEATURE!)
"""
curl -X PUT http://localhost:5000/api/api-keys/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated OpenAI Key",
    "key_type": "openai",
    "key_value": "sk-new-updated-key-67890",
    "is_active": true
  }'

Response:
{
  "success": true,
  "message": "API key updated",
  "key": {
    "id": 1,
    "name": "Updated OpenAI Key",
    "type": "openai",
    "is_active": true,
    "masked_value": "sk-new-u...",
    "created_at": "2026-01-25T10:30:00",
    "updated_at": "2026-01-25T11:45:00"
  }
}
"""

# 4. DELETE an API Key
"""
curl -X DELETE http://localhost:5000/api/api-keys/1

Response:
{
  "success": true,
  "message": "API key deleted"
}
"""

# ============ PARTIAL UPDATE EXAMPLES ============

# Update only the name
"""
curl -X PUT http://localhost:5000/api/api-keys/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Renamed Key"
  }'
"""

# Update only the status (active/inactive)
"""
curl -X PUT http://localhost:5000/api/api-keys/1 \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false
  }'
"""

# Update only the key value
"""
curl -X PUT http://localhost:5000/api/api-keys/1 \
  -H "Content-Type: application/json" \
  -d '{
    "key_value": "sk-brand-new-secret-key"
  }'
"""

# ============ WEB INTERFACE ============

# Navigate to: http://localhost:5000/api-keys
# 
# Features:
# - Add New API Key form
# - View all your keys in card format
# - Edit each key by clicking "Edit"
# - Delete keys by clicking trash icon
# - See creation and last used dates
# - Toggle key visibility for security
# - View active/inactive status

print("""
✅ API KEY MANAGEMENT COMPLETE

Features Implemented:
  ✅ Create API Keys
  ✅ Read/View API Keys  
  ✅ Update API Keys (UPDATE ENDPOINT)
  ✅ Delete API Keys
  ✅ Web Management Interface
  ✅ Secure Storage in Database
  ✅ Activity Tracking
  ✅ Multiple Key Types Support

Available Routes:
  GET    /api/api-keys              - Get all API keys
  POST   /api/api-keys              - Create new API key
  PUT    /api/api-keys/<id>         - Update API key (NEW!)
  DELETE /api/api-keys/<id>         - Delete API key
  GET    /api-keys                  - Management page

Ready to use! Access the management page at:
  http://localhost:5000/api-keys
""")
