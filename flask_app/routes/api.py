"""
API Routes for Backend Functionality
"""
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from flask_app import db
from flask_app.models import SavedConfig, APIKey, JiraXraySettings
from flask_app.agents import get_agent_manager, create_agent_id
from datetime import datetime
import json
import asyncio
import logging
logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)


# ============ Configuration API Routes ============

@api_bp.route('/configs', methods=['GET'])
@login_required
def get_configs():
    """Get all saved configurations"""
    config_type = request.args.get('type', 'agent')
    
    configs = SavedConfig.query.filter_by(
        user_id=current_user.id,
        config_type=config_type
    ).all()
    
    return jsonify({
        'success': True,
        'configs': [{
            'id': c.id,
            'name': c.config_name,
            'type': c.config_type,
            'description': c.description,
            'is_favorite': c.is_favorite,
            'created_at': c.created_at.isoformat(),
            'updated_at': c.updated_at.isoformat()
        } for c in configs]
    })


@api_bp.route('/configs', methods=['POST'])
@login_required
def save_config():
    """Save a new configuration"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'type' not in data:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    try:
        config = SavedConfig(
            user_id=current_user.id,
            config_name=data['name'],
            config_type=data['type'],
            config_data=data.get('config_data', {}),
            description=data.get('description', '')
        )
        
        db.session.add(config)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'config': {
                'id': config.id,
                'name': config.config_name,
                'type': config.config_type
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/configs/<int:config_id>', methods=['GET'])
@login_required
def get_config(config_id):
    """Get specific configuration"""
    config = SavedConfig.query.filter_by(
        id=config_id,
        user_id=current_user.id
    ).first()
    
    if not config:
        return jsonify({'success': False, 'error': 'Configuration not found'}), 404
    
    return jsonify({
        'success': True,
        'config': {
            'id': config.id,
            'name': config.config_name,
            'type': config.config_type,
            'data': config.config_data,
            'description': config.description,
            'is_favorite': config.is_favorite
        }
    })


@api_bp.route('/configs/<int:config_id>', methods=['PUT'])
@login_required
def update_config(config_id):
    """Update configuration"""
    config = SavedConfig.query.filter_by(
        id=config_id,
        user_id=current_user.id
    ).first()
    
    if not config:
        return jsonify({'success': False, 'error': 'Configuration not found'}), 404
    
    data = request.get_json()
    
    try:
        if 'name' in data:
            config.config_name = data['name']
        if 'description' in data:
            config.description = data['description']
        if 'config_data' in data:
            config.config_data = data['config_data']
        if 'is_favorite' in data:
            config.is_favorite = data['is_favorite']
        
        config.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Configuration updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/configs/<int:config_id>', methods=['DELETE'])
@login_required
def delete_config(config_id):
    """Delete configuration"""
    config = SavedConfig.query.filter_by(
        id=config_id,
        user_id=current_user.id
    ).first()
    
    if not config:
        return jsonify({'success': False, 'error': 'Configuration not found'}), 404
    
    try:
        db.session.delete(config)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Configuration deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============ Agent Execution API Routes (Deprecated - See Agent Execution Routes section below) ============
# Placeholder routes - use the full implementation in the Agent Execution Routes section below


# ============ API Key Management Routes ============

@api_bp.route('/api-keys', methods=['GET'])
@login_required
def get_api_keys():
    """Get user's API keys (masked)"""
    keys = APIKey.query.filter_by(user_id=current_user.id).all()
    
    return jsonify({
        'success': True,
        'api_keys': [{
            'id': k.id,
            'name': k.key_name,
            'type': k.key_type,
            'is_active': k.is_active,
            'masked_value': k.key_value[:8] + '...',
            'last_used': k.last_used.isoformat() if k.last_used else None,
            'created_at': k.created_at.isoformat()
        } for k in keys]
    })


@api_bp.route('/api-keys', methods=['POST'])
@login_required
def create_api_key():
    """Create new API key"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'key_value' not in data:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    try:
        key = APIKey(
            user_id=current_user.id,
            key_name=data['name'],
            key_value=data['key_value'],
            key_type=data.get('key_type', 'api_key')
        )
        
        db.session.add(key)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'API key created',
            'key_id': key.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/api-keys/<int:key_id>', methods=['PUT'])
@login_required
def update_api_key(key_id):
    """Update API key"""
    key = APIKey.query.filter_by(
        id=key_id,
        user_id=current_user.id
    ).first()
    
    if not key:
        return jsonify({'success': False, 'error': 'API key not found'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    try:
        # Update key name if provided
        if 'name' in data:
            key.key_name = data['name']
        
        # Update key value if provided
        if 'key_value' in data:
            key.key_value = data['key_value']
        
        # Update key type if provided
        if 'key_type' in data:
            key.key_type = data['key_type']
        
        # Update active status if provided
        if 'is_active' in data:
            key.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'API key updated',
            'key': {
                'id': key.id,
                'name': key.key_name,
                'type': key.key_type,
                'is_active': key.is_active,
                'masked_value': key.key_value[:8] + '...',
                'created_at': key.created_at.isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/api-keys/<int:key_id>', methods=['DELETE'])
@login_required
def delete_api_key(key_id):
    """Delete API key"""
    key = APIKey.query.filter_by(
        id=key_id,
        user_id=current_user.id
    ).first()
    
    if not key:
        return jsonify({'success': False, 'error': 'API key not found'}), 404
    
    try:
        db.session.delete(key)
        db.session.commit()
        return jsonify({'success': True, 'message': 'API key deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============ Agent Execution Routes ============

@api_bp.route('/run-agent', methods=['POST'], endpoint='execute_agent_task')
@login_required
def run_agent():
    """
    Execute an AI agent with the given task.
    
    Request body:
    {
        "agent_type": "browser_use" or "deep_research",
        "task": "What you want the agent to do",
        "provider": "openai" or "ollama",
        "model": "gpt-4" or "llama2",
        "api_key": "optional-override-api-key",
        "temperature": 0.7,
        "headless": true
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['agent_type', 'task', 'provider', 'model']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {required_fields}'
            }), 400
        
        # Create agent execution ID
        agent_id = create_agent_id()
        
        # Get or use provided API key
        api_key = data.get('api_key')
        if not api_key:
            # Try to get from user's saved keys
            saved_key = APIKey.query.filter_by(
                user_id=current_user.id,
                key_type=data['provider']
            ).first()
            if saved_key:
                api_key = saved_key.key_value
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': f'No API key found for provider: {data["provider"]}'
            }), 400
        
        # Get agent manager
        agent_manager = get_agent_manager()
        
        # Prepare agent configuration
        agent_config = {
            'provider': data['provider'],
            'model': data['model'],
            'api_key': api_key,
            'temperature': data.get('temperature', 0.7),
            'base_url': data.get('base_url'),
            'headless': data.get('headless', True),
            'viewport': data.get('viewport', {'width': 1920, 'height': 1080}),
        }
        
        # Run agent asynchronously (for now, run synchronously)
        # In production, use Celery for background tasks
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            agent_manager.run_agent_async(
                agent_id=agent_id,
                agent_type=data['agent_type'],
                task=data['task'],
                user_id=current_user.id,
                **agent_config
            )
        )
        
        if result['success']:
            # Save execution to database
            try:
                config = SavedConfig(
                    user_id=current_user.id,
                    config_name=f"Execution: {agent_id[:8]}",
                    config_type='agent_execution',
                    config_data=json.dumps(result['data']),
                    description=f"Agent: {data['agent_type']}, Task: {data['task'][:50]}..."
                )
                db.session.add(config)
                db.session.commit()
            except Exception as e:
                logger.error(f"Failed to save agent execution to DB: {e}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in run-agent endpoint: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/agent-status/<agent_id>', methods=['GET'])
@login_required
def agent_status(agent_id):
    """Get status of a running agent"""
    try:
        agent_manager = get_agent_manager()
        status = agent_manager.get_agent_status(agent_id)
        
        return jsonify({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/agent-stop/<agent_id>', methods=['POST'])
@login_required
def stop_agent(agent_id):
    """Stop a running agent"""
    try:
        agent_manager = get_agent_manager()
        result = agent_manager.stop_agent(agent_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error stopping agent: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/agent-history', methods=['GET'])
@login_required
def agent_history():
    """Get agent execution history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        agent_manager = get_agent_manager()
        
        history = agent_manager.get_execution_history(current_user.id, limit=limit)
        
        return jsonify({
            'success': True,
            'data': history
        })
        
    except Exception as e:
        logger.error(f"Error getting agent history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============ Model & Settings API Routes ============

@api_bp.route('/settings/model', methods=['POST'])
@login_required
def save_model_settings():
    """Save model selection and settings"""
    data = request.get_json()
    
    try:
        # Create or update model settings config
        config_data = {
            'provider': data.get('provider'),
            'model': data.get('model'),
            'temperature': data.get('temperature', 0.7),
            'max_tokens': data.get('max_tokens', 2000),
            'system_prompt': data.get('system_prompt', ''),
            'use_streaming': data.get('use_streaming', False)
        }
        
        # Check if model config already exists
        model_config = SavedConfig.query.filter_by(
            user_id=current_user.id,
            config_name='model_settings',
            config_type='model'
        ).first()
        
        if model_config:
            model_config.config_data = config_data
            model_config.updated_at = datetime.utcnow()
        else:
            model_config = SavedConfig(
                user_id=current_user.id,
                config_name='model_settings',
                config_type='model',
                config_data=config_data,
                description='LLM Model Configuration'
            )
            db.session.add(model_config)
        
        db.session.commit()
        
        # Log the action
        log_setting_change('model', f"Changed to {data.get('provider')} - {data.get('model')}")
        
        return jsonify({
            'success': True,
            'message': 'Model settings saved successfully',
            'config': {
                'id': model_config.id,
                'provider': config_data['provider'],
                'model': config_data['model']
            }
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving model settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/settings/model', methods=['GET'])
@login_required
def get_model_settings():
    """Get current model settings"""
    try:
        model_config = SavedConfig.query.filter_by(
            user_id=current_user.id,
            config_name='model_settings',
            config_type='model'
        ).first()
        
        if model_config:
            return jsonify({
                'success': True,
                'settings': model_config.config_data
            })
        else:
            return jsonify({
                'success': True,
                'settings': {
                    'provider': 'openai',
                    'model': 'gpt-4o',
                    'temperature': 0.7,
                    'max_tokens': 2000,
                    'system_prompt': '',
                    'use_streaming': False
                }
            })
    except Exception as e:
        logger.error(f"Error getting model settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/settings/history', methods=['GET'])
@login_required
def get_settings_history():
    """Get settings change history"""
    try:
        # Get history from settings_log table or config changes
        history_config = SavedConfig.query.filter_by(
            user_id=current_user.id,
            config_name='settings_history',
            config_type='history'
        ).first()
        
        if history_config:
            history = history_config.config_data.get('changes', [])
            # Sort by timestamp, most recent first
            history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return jsonify({
                'success': True,
                'history': history[:50]  # Return last 50 changes
            })
        else:
            return jsonify({
                'success': True,
                'history': []
            })
    except Exception as e:
        logger.error(f"Error getting settings history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============ Helper Functions ============

def log_setting_change(setting_type, changes):
    """Log a settings change"""
    try:
        history_config = SavedConfig.query.filter_by(
            user_id=current_user.id,
            config_name='settings_history',
            config_type='history'
        ).first()
        
        if not history_config:
            history_config = SavedConfig(
                user_id=current_user.id,
                config_name='settings_history',
                config_type='history',
                config_data={'changes': []},
                description='Settings Change History'
            )
            db.session.add(history_config)
        
        history_list = history_config.config_data.get('changes', [])
        history_list.append({
            'timestamp': datetime.utcnow().isoformat(),
            'setting_type': setting_type,
            'changes': changes,
            'action': 'Updated'
        })
        
        history_config.config_data['changes'] = history_list
        db.session.commit()
    except Exception as e:
        logger.error(f"Error logging setting change: {e}")
        db.session.rollback()


# ============ Code Generator API Routes ============

@api_bp.route('/code-generator/agent-settings', methods=['GET'])
@login_required
def get_agent_settings_for_generator():
    """Get agent settings with LLM model and API keys for code generator"""
    try:
        # Try agent_settings table first
        try:
            result = db.session.execute(
                db.text("""
                    SELECT id, setting_name, settings_data  
                    FROM agent_settings
                    WHERE user_id = :user_id
                    ORDER BY setting_name ASC
                """),
                {'user_id': current_user.id}
            )
            print(result)
            rows = result.fetchall()


            settings_list = []
            for row in rows:
                config_data = json.loads(row[2])

                # Extract values from parsed JSON
                llm_provider = config_data.get('llm_provider', '')
                llm_model_name = config_data.get('llm_model_name', '')
                llm_temperature = config_data.get('llm_temperature', 0.0)
                llm_api_key = config_data.get('llm_api_key', '')
                settings_list.append({
                    'id': row[0],
                    'name': row[1],
                    'llm_provider':llm_provider ,
                    'llm_model_name': llm_model_name,
                    'llm_temperature': llm_temperature,
                    'description': row[1],
                    'llm_api_key' :llm_api_key
                })

            logger.info(f"Found {len(settings_list)} agent settings for user {current_user.id}")

            # Get API keys
            api_keys = APIKey.query.filter_by(
                user_id=current_user.id,
                is_active=True
            ).all()



            return jsonify({
                'success': True,
                'agent_settings': settings_list,
                'api_keys': llm_api_key
            })

        except Exception as db_error:
            logger.warning(f"agent_settings query failed: {db_error}")
            # Fallback to SavedConfig
            configs = SavedConfig.query.filter_by(
                user_id=current_user.id,
                config_type='agent'
            ).all()

            settings_list = []
            for config in configs:
                config_data = config.config_data or {}
                settings_list.append({
                    'id': config.id,
                    'name': config.config_name,
                    'llm_provider': config_data.get('llm_provider', 'openai'),
                    'llm_model_name': config_data.get('llm_model_name', 'gpt-3.5-turbo'),
                    'llm_temperature': config_data.get('llm_temperature', 0.6),
                    'description': config.description
                })

            api_keys = APIKey.query.filter_by(
                user_id=current_user.id,
                is_active=True
            ).all()

            api_keys_list = [{
                'id': key.id,
                'name': key.key_name,
                'type': key.key_type,
                'value': key.key_value[:10] + '...' if len(key.key_value) > 10 else key.key_value
            } for key in api_keys]

            return jsonify({
                'success': True,
                'agent_settings': settings_list,
                'api_keys': api_keys_list
            })

    except Exception as e:
        logger.error(f"Error fetching agent settings: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/code-generator/agents', methods=['GET'])
@login_required
def get_all_agents():
    """Get all agents for the current user from agent_settings table, fallback to SavedConfig."""
    try:
        logger.info(f"Fetching agents for user {current_user.id}")
        try:
            result = db.session.execute(
                db.text("""
                    SELECT id, setting_name, settings_data 
                    FROM agent_settings
                    WHERE user_id = :user_id
                    ORDER BY id DESC
                """),
                {'user_id': current_user.id}
            )
            rows = result.fetchall()
            agents_list = []
            for row in rows:
                config_data = json.loads(row[2])

                # Extract values from parsed JSON
                llm_provider = config_data.get('llm_provider', '')
                llm_model_name = config_data.get('llm_model_name', '')
                llm_temperature = config_data.get('llm_temperature', 0.0)
                llm_api_key = config_data.get('llm_api_key', '')
                agents_list.append({
                    'id': row[0],
                    'name': row[1],
                    'llm_provider': llm_provider,
                    'llm_model_name': llm_model_name,
                    'llm_temperature': llm_temperature,
                    'description': row[1],
                    'llm_api_key': llm_api_key
                })
            logger.info(f"Found {len(agents_list)} agents from agent_settings for user {current_user.id}")
            return jsonify({
                'success': True,
                'agents': agents_list,
                'total': len(agents_list),
                'source': 'agent_settings'
            })
        except Exception as db_error:
            logger.error(f"Database error querying agent_settings: {db_error}", exc_info=True)
            # Fallback to SavedConfig table
            configs = SavedConfig.query.filter_by(
                user_id=current_user.id,
                config_type='agent'
            ).all()
            agents_list = []
            for config in configs:
                config_data = config.config_data or {}
                agents_list.append({
                    'id': config.id,
                    'name': config.config_name,
                    'llm_provider': config_data.get('llm_provider', 'openai'),
                    'llm_model_name': config_data.get('llm_model_name', 'gpt-3.5-turbo'),
                    'llm_api_key': config_data.get('llm_api_key', ''),
                    'description': config.description or ''
                })
            logger.info(f"Found {len(agents_list)} agents from SavedConfig for user {current_user.id}")
            return jsonify({
                'success': True,
                'agents': agents_list,
                'total': len(agents_list),
                'source': 'saved_config'
            })
    except Exception as e:
        logger.error(f"Error fetching agents: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/code-generator/agent/<int:agent_id>', methods=['GET'])
@login_required
def get_agent_details(agent_id):
    """Get specific agent details with LLM model and API key"""
    try:
        logger.info(f"Fetching agent {agent_id} for user {current_user.id}")
        try:
            result = db.session.execute(
                db.text("""
                    SELECT id, setting_name, settings_data 
                    FROM agent_settings
                    WHERE id = :agent_id AND user_id = :user_id
                """),
                {'agent_id': agent_id, 'user_id': current_user.id}
            )
            row = result.fetchone()
            config_data = json.loads(row[2])
            if row:
                return jsonify({
                    'success': True,
                    'agent': {
                        'id': row[0],
                        'name': row[1] if row[1] else f'Agent {row[0]}',
                        'llm_provider': config_data.get('llm_provider', ''),
                        'llm_model_name': config_data.get('llm_model_name', ''),
                        'llm_temperature': config_data.get('llm_temperature', 0.0),
                        'llm_api_key': config_data.get('llm_api_key', ''),
                        'llm_base_url': "",
                        'description': row[1]
                    }
                })
        except Exception as db_error:
            logger.warning(f"agent_settings query failed: {db_error}, trying SavedConfig...")
        config = SavedConfig.query.filter_by(
            id=agent_id,
            user_id=current_user.id,
            config_type='agent'
        ).first()
        if not config:
            return jsonify({'success': False, 'error': 'Agent not found'}), 404
        config_data = config.config_data or {}
        return jsonify({
            'success': True,
            'agent': {
                'id': config.id,
                'name': config.config_name,
                'llm_provider': config_data.get('llm_provider', 'openai'),
                'llm_model_name': config_data.get('llm_model_name', 'gpt-3.5-turbo'),
                'llm_temperature': config_data.get('llm_temperature', 0.7),
                'llm_api_key': config_data.get('llm_api_key', ''),
                'llm_base_url': config_data.get('llm_base_url', ''),
                'description': config.description or ''
            }
        })
    except Exception as e:
        logger.error(f"Error fetching agent details: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/code-generator/create-test-agent', methods=['POST'])
@login_required
def create_test_agent():
    """Create a test agent for the current user"""
    try:
        logger.info(f"Creating test agent for user {current_user.id}")
        try:
            db.session.execute(
                db.text("""
                    INSERT INTO agent_settings 
                    (user_id, setting_name, llm_provider, llm_model_name, llm_temperature, llm_api_key, description)
                    VALUES (:user_id, :setting_name, :llm_provider, :llm_model_name, :llm_temperature, :llm_api_key, :description)
                """),
                {
                    'user_id': current_user.id,
                    'setting_name': f'Test Agent - {current_user.username}',
                    'llm_provider': 'openai',
                    'llm_model_name': 'gpt-3.5-turbo',
                    'llm_temperature': 0.7,
                    'llm_api_key': 'sk-test-key-placeholder',
                    'description': 'Test agent created for code generator'
                }
            )
            db.session.commit()
            result = db.session.execute(db.text("SELECT LAST_INSERT_ID()"))
            new_agent_id = result.fetchone()[0]
            logger.info(f"Created test agent {new_agent_id} in agent_settings for user {current_user.id}")
            return jsonify({
                'success': True,
                'message': 'Test agent created',
                'agent_id': new_agent_id
            })
        except Exception as db_error:
            db.session.rollback()
            logger.warning(f"agent_settings insert failed: {db_error}, trying SavedConfig...")
            config = SavedConfig(
                user_id=current_user.id,
                config_name=f'Test Agent - {current_user.username}',
                config_type='agent',
                config_data={
                    'llm_provider': 'openai',
                    'llm_model_name': 'gpt-3.5-turbo',
                    'llm_temperature': 0.7,
                    'llm_api_key': 'sk-test-key-placeholder'
                },
                description='Test agent created for code generator'
            )
            db.session.add(config)
            db.session.commit()
            logger.info(f"Created test agent {config.id} in SavedConfig for user {current_user.id}")
            return jsonify({
                'success': True,
                'message': 'Test agent created',
                'agent_id': config.id
            })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating test agent: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/code-generator/create-agent-with-config', methods=['POST'])
@login_required
def create_agent_with_config():
    """Create or update agent with framework, language, and scenario configuration"""
    try:
        data = request.get_json()
        logger.info(f"Creating/updating agent with config: {json.dumps(data, indent=2)}")
        required_fields = ['model_name', 'llm_provider', 'llm_api_key', 'framework', 'language']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            logger.error(error_msg)
            return jsonify({'success': False, 'error': error_msg}), 400
        agent_name = f"{data.get('framework', 'Test')} - {data.get('language', 'JS')} ({data.get('model_name', 'unknown')})"
        scenario = data.get('scenario', '')
        description = f"Framework: {data.get('framework')}\nLanguage: {data.get('language')}\n\nScenario:\n{scenario[:500]}"
        try:
            result = db.session.execute(
                db.text("""
                    SELECT id FROM agent_settings 
                    WHERE user_id = :user_id AND setting_name = :setting_name
                """),
                {'user_id': current_user.id, 'setting_name': agent_name}
            )
            existing = result.fetchone()
            if existing:
                db.session.execute(
                    db.text("""
                        UPDATE agent_settings 
                        SET llm_provider = :llm_provider, 
                            llm_model_name = :llm_model_name, 
                            llm_temperature = :llm_temperature, 
                            llm_api_key = :llm_api_key, 
                            description = :description
                        WHERE id = :id AND user_id = :user_id
                    """),
                    {
                        'llm_provider': data.get('llm_provider'),
                        'llm_model_name': data.get('model_name'),
                        'llm_temperature': data.get('temperature', 0.7),
                        'llm_api_key': data.get('llm_api_key'),
                        'description': description,
                        'id': existing[0],
                        'user_id': current_user.id
                    }
                )
                db.session.commit()
                new_agent_id = existing[0]
                action = 'updated'
            else:
                db.session.execute(
                    db.text("""
                        INSERT INTO agent_settings 
                        (user_id, setting_name, llm_provider, llm_model_name, llm_temperature, llm_api_key, description)
                        VALUES (:user_id, :setting_name, :llm_provider, :llm_model_name, :llm_temperature, :llm_api_key, :description)
                    """),
                    {
                        'user_id': current_user.id,
                        'setting_name': agent_name,
                        'llm_provider': data.get('llm_provider'),
                        'llm_model_name': data.get('model_name'),
                        'llm_temperature': data.get('temperature', 0.7),
                        'llm_api_key': data.get('llm_api_key'),
                        'description': description
                    }
                )
                db.session.commit()
                result = db.session.execute(db.text("SELECT LAST_INSERT_ID()"))
                new_agent_id = result.fetchone()[0]
                action = 'created'
            logger.info(f"✅ Agent {action}: {new_agent_id}")
            return jsonify({
                'success': True,
                'message': f'Agent {action} successfully',
                'action': action,
                'agent_id': new_agent_id,
                'agent': {
                    'id': new_agent_id,
                    'name': agent_name,
                    'llm_provider': data.get('llm_provider'),
                    'llm_model_name': data.get('model_name'),
                    'llm_api_key': data.get('llm_api_key')
                }
            })
        except Exception as db_error:
            db.session.rollback()
            logger.warning(f"agent_settings failed: {db_error}, using SavedConfig...")
            config = SavedConfig.query.filter_by(
                user_id=current_user.id,
                config_name=agent_name,
                config_type='agent'
            ).first()
            config_data = {
                'llm_provider': data.get('llm_provider'),
                'llm_model_name': data.get('model_name'),
                'llm_temperature': data.get('temperature', 0.7),
                'llm_api_key': data.get('llm_api_key')
            }
            if config:
                config.config_data = config_data
                config.description = description
                config.updated_at = datetime.utcnow()
                action = 'updated'
            else:
                config = SavedConfig(
                    user_id=current_user.id,
                    config_name=agent_name,
                    config_type='agent',
                    config_data=config_data,
                    description=description
                )
                db.session.add(config)
                action = 'created'
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'Agent {action} successfully',
                'action': action,
                'agent_id': config.id,
                'agent': {
                    'id': config.id,
                    'name': agent_name,
                    'llm_provider': data.get('llm_provider'),
                    'llm_model_name': data.get('model_name'),
                    'llm_api_key': data.get('llm_api_key')
                }
            })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating/updating agent: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# ============ Jira-Xray Settings API Routes ============

@api_bp.route('/jira-xray-settings', methods=['GET'])
@login_required
def get_jira_xray_settings():
    """Get all Jira-Xray settings for current user"""
    try:
        settings = JiraXraySettings.query.filter_by(user_id=current_user.id).all()
        return jsonify({
            'success': True,
            'settings': [s.to_dict() for s in settings]
        })
    except Exception as e:
        logger.error(f"Error fetching Jira-Xray settings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/jira-xray-settings', methods=['POST'])
@login_required
def create_jira_xray_settings():
    """Create new Jira-Xray settings"""
    try:
        data = request.get_json()
        # Validate required fields
        required_fields = [
            'jira_requirement_key', 'jira_username', 'jira_url',
        ]
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create new settings
        settings = JiraXraySettings(
            user_id=current_user.id,
            jira_requirement_key=data['jira_requirement_key'],
            jira_username=data['jira_username'],
            jira_url=data['jira_url'],
            jira_api_token=data.get('jira_api_token'),
            project_key=data['project_key'],
            version_name=data['version_name'],
            xray_folder_path=data['xray_folder_path'],
            xray_client_id=data.get('xray_client_id'),
            xray_client_secret=data.get('xray_client_secret'),
            num_test_cases=int(data.get('num_test_cases', 1)),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(settings)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Jira-Xray settings created successfully',
            'settings': settings.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating Jira-Xray settings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/jira-xray-settings/<int:settings_id>', methods=['GET'])
@login_required
def get_jira_xray_setting(settings_id):
    """Get specific Jira-Xray setting"""
    try:
        settings = JiraXraySettings.query.filter_by(
            id=settings_id,
            user_id=current_user.id
        ).first()
        if not settings:
            return jsonify({'success': False, 'error': 'Settings not found'}), 404
                
        return jsonify({
            'success': True,
            'settings': settings.to_dict(include_secrets=True)
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error fetching Jira-Xray settings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/jira-xray-settings/<int:settings_id>', methods=['PUT'])
@login_required
def update_jira_xray_settings(settings_id):
    """Update existing Jira-Xray settings"""
    data = request.get_json() or {}

    try:
        settings = JiraXraySettings.query.filter_by(
            id=settings_id,
            user_id=current_user.id
        ).first()
        if not settings:
            return jsonify({'success': False, 'error': 'Settings not found'}), 404
        # Update fields
        if 'jira_requirement_key' in data:
            settings.jira_requirement_key = data['jira_requirement_key']
        if 'jira_username' in data:
            settings.jira_username = data['jira_username']
        if 'jira_url' in data:
            settings.jira_url = data['jira_url']
        if 'jira_api_token' in data:
            settings.jira_api_token = data['jira_api_token']
        if 'project_key' in data:
            settings.project_key = data['project_key']
        if 'version_name' in data:
            settings.version_name = data['version_name']
        if 'xray_folder_path' in data:
            settings.xray_folder_path = data['xray_folder_path']
        if 'xray_client_id' in data:
            settings.xray_client_id = data['xray_client_id']
        if 'xray_client_secret' in data:
            settings.xray_client_secret = data['xray_client_secret']
        if 'num_test_cases' in data:
            settings.num_test_cases = int(data['num_test_cases'])
        if 'is_active' in data:
            settings.is_active = data['is_active']
        settings.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Jira-Xray settings updated successfully',
            'settings': settings.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating Jira-Xray settings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/jira-xray-settings/<int:settings_id>', methods=['DELETE'])
@login_required
def delete_jira_xray_settings(settings_id):
    """Delete Jira-Xray settings"""
    try:
        settings = JiraXraySettings.query.filter_by(
            id=settings_id,
            user_id=current_user.id
        ).first()
        if not settings:
            return jsonify({'success': False, 'error': 'Settings not found'}), 404
        db.session.delete(settings)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Jira-Xray settings deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============ Test Case Generation API Routes ============

@api_bp.route('/generate-test-cases', methods=['POST'])
@login_required
def generate_test_cases():
    """Generate test cases from Jira requirement"""
    try:
        data = request.get_json()
        # Validate required fields
        required_fields = ['project_key', 'num_test_cases', 'requirement_key']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Import the test case generation module
        from flask_app.generate_tcs_for_issue import generate_with_openai, main
        # Extract parameters
        project_key = data.get('project_key')
        num_test_cases = int(data.get('num_test_cases', 1))
        requirement_key = data.get('requirement_key')
        jira_url = data.get('jira_url', '').rstrip('/')
        username = data.get('username')
        version_name = data.get('version_name', '')
        folder_path = data.get('folder_path', '')
        
        # Validate Jira URL
        if not jira_url.startswith(('http://', 'https://')):
            return jsonify({
                'success': False,
                'error': 'Invalid Jira URL format'
            }), 400
        
        # Extract base URL (without /rest/api)
        base_url = jira_url.rstrip('/') + '/rest/api/3'
        
        # Call the test case generation function with Flask app context
        result = main(
            req=requirement_key,
            username=username,
            baseurl=base_url,
            project_key=project_key,
            version_name=version_name,
            folder_path=folder_path,
            tc_amount=num_test_cases,
            skip_checks=False,
            del_tc=False,
            debug=True,
            app=current_app
        )
        
        return jsonify({
            'success': True,
            'message': f'Generated {num_test_cases} test cases successfully',
            'result': result
        })
        
    except ImportError as e:
        logger.error(f"Import error in generate_test_cases: {e}")
        return jsonify({
            'success': False,
            'error': 'Test case generation module not available'
        }), 500
    except Exception as e:
        logger.error(f"Error generating test cases: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============ Health Check ============

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })
