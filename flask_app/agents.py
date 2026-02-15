"""
Agent wrapper module for Flask integration.
Bridges the Gradio agents to Flask API endpoints.
"""

import asyncio
import json
import logging
import uuid
from typing import Optional, Dict, Any
from datetime import datetime

from src.agent.browser_use.browser_use_agent import BrowserUseAgent
from src.agent.deep_research.deep_research_agent import DeepResearchAgent
from src.utils.llm_provider import get_llm_model
from src.browser.custom_browser import CustomBrowser
from src.controller.custom_controller import CustomController

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages agent execution and lifecycle."""
    
    def __init__(self):
        self.active_agents = {}  # Store running agents
        self.execution_history = {}  # Store execution results
    
    def create_browser_use_agent(
        self,
        provider: str,
        model: str,
        api_key: str,
        temperature: float = 0.7,
        base_url: Optional[str] = None,
        **kwargs
    ) -> Optional[BrowserUseAgent]:
        """Create a Browser Use agent."""
        try:
            # Initialize LLM
            llm = get_llm_model(
                provider=provider,
                model_name=model,
                api_key=api_key,
                temperature=temperature,
                base_url=base_url,
                num_ctx=kwargs.get('num_ctx'),
            )
            
            if not llm:
                logger.error(f"Failed to initialize LLM: {provider}/{model}")
                return None
            
            # Create browser config
            browser_config = {
                'headless': kwargs.get('headless', True),
                'viewport': kwargs.get('viewport', {'width': 1920, 'height': 1080}),
                'disable_images': kwargs.get('disable_images', False),
            }
            
            # Initialize agent
            agent = BrowserUseAgent(
                llm=llm,
                browser_config=browser_config,
                **kwargs
            )
            
            logger.info(f"Browser Use agent created: {provider}/{model}")
            return agent
            
        except Exception as e:
            logger.error(f"Error creating Browser Use agent: {e}", exc_info=True)
            return None
    
    def create_deep_research_agent(
        self,
        provider: str,
        model: str,
        api_key: str,
        temperature: float = 0.7,
        base_url: Optional[str] = None,
        **kwargs
    ) -> Optional[DeepResearchAgent]:
        """Create a Deep Research agent."""
        try:
            # Initialize LLM
            llm = get_llm_model(
                provider=provider,
                model_name=model,
                api_key=api_key,
                temperature=temperature,
                base_url=base_url,
                num_ctx=kwargs.get('num_ctx'),
            )
            
            if not llm:
                logger.error(f"Failed to initialize LLM: {provider}/{model}")
                return None
            
            # Initialize agent
            agent = DeepResearchAgent(
                llm=llm,
                **kwargs
            )
            
            logger.info(f"Deep Research agent created: {provider}/{model}")
            return agent
            
        except Exception as e:
            logger.error(f"Error creating Deep Research agent: {e}", exc_info=True)
            return None
    
    async def run_agent_async(
        self,
        agent_id: str,
        agent_type: str,
        task: str,
        user_id: int,
        **agent_config
    ) -> Dict[str, Any]:
        """Run agent asynchronously and return results."""
        try:
            # Create appropriate agent
            if agent_type == 'browser_use':
                agent = self.create_browser_use_agent(**agent_config)
            elif agent_type == 'deep_research':
                agent = self.create_deep_research_agent(**agent_config)
            else:
                raise ValueError(f"Unknown agent type: {agent_type}")
            
            if not agent:
                return {
                    'success': False,
                    'error': 'Failed to create agent',
                    'agent_id': agent_id,
                }
            
            # Store agent reference
            self.active_agents[agent_id] = {
                'agent': agent,
                'type': agent_type,
                'user_id': user_id,
                'started_at': datetime.utcnow(),
                'status': 'running',
            }
            
            logger.info(f"Starting agent execution: {agent_id} ({agent_type})")
            
            # Run agent
            result = await agent.run_async(task)
            
            # Store execution result
            execution_result = {
                'agent_id': agent_id,
                'agent_type': agent_type,
                'task': task,
                'result': result,
                'status': 'completed',
                'started_at': self.active_agents[agent_id]['started_at'],
                'completed_at': datetime.utcnow(),
                'duration': (datetime.utcnow() - self.active_agents[agent_id]['started_at']).total_seconds(),
            }
            
            self.execution_history[agent_id] = execution_result
            self.active_agents[agent_id]['status'] = 'completed'
            
            logger.info(f"Agent execution completed: {agent_id}")
            
            return {
                'success': True,
                'data': execution_result,
                'agent_id': agent_id,
            }
            
        except Exception as e:
            logger.error(f"Error during agent execution: {e}", exc_info=True)
            
            if agent_id in self.active_agents:
                self.active_agents[agent_id]['status'] = 'failed'
                self.active_agents[agent_id]['error'] = str(e)
            
            return {
                'success': False,
                'error': str(e),
                'agent_id': agent_id,
            }
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status of running agent."""
        if agent_id not in self.active_agents:
            return {
                'status': 'not_found',
                'agent_id': agent_id,
            }
        
        agent_info = self.active_agents[agent_id]
        return {
            'agent_id': agent_id,
            'status': agent_info['status'],
            'type': agent_info['type'],
            'started_at': agent_info['started_at'],
            'duration': (datetime.utcnow() - agent_info['started_at']).total_seconds(),
        }
    
    def get_execution_history(self, user_id: int, limit: int = 10) -> list:
        """Get execution history for a user."""
        user_executions = [
            execution for execution in self.execution_history.values()
            if execution.get('user_id') == user_id
        ]
        return user_executions[-limit:]
    
    def stop_agent(self, agent_id: str) -> Dict[str, Any]:
        """Stop a running agent."""
        if agent_id not in self.active_agents:
            return {
                'success': False,
                'error': 'Agent not found',
                'agent_id': agent_id,
            }
        
        try:
            agent_info = self.active_agents[agent_id]
            agent = agent_info['agent']
            
            # Stop agent if it has a stop method
            if hasattr(agent, 'stop'):
                agent.stop()
            
            agent_info['status'] = 'stopped'
            agent_info['stopped_at'] = datetime.utcnow()
            
            logger.info(f"Agent stopped: {agent_id}")
            
            return {
                'success': True,
                'agent_id': agent_id,
            }
            
        except Exception as e:
            logger.error(f"Error stopping agent: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'agent_id': agent_id,
            }


# Global agent manager instance
_agent_manager = None


def get_agent_manager() -> AgentManager:
    """Get or create global agent manager."""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = AgentManager()
    return _agent_manager


def create_agent_id() -> str:
    """Generate unique agent execution ID."""
    return str(uuid.uuid4())
