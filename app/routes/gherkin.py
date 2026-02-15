from flask import Blueprint, request, jsonify
from app.models import Agent
from app.database import db
import anthropic

gherkin_bp = Blueprint('gherkin', __name__, url_prefix='/api')

@gherkin_bp.route('/agents', methods=['GET'])
def get_agents():
    """Fetch all saved agents from database"""
    agents = Agent.query.all()
    return jsonify([{
        'id': agent.id,
        'name': agent.name,
        'model': agent.model
    } for agent in agents])

@gherkin_bp.route('/generate-gherkin', methods=['POST'])
def generate_gherkin():
    """Generate Gherkin from manual scenario using selected agent"""
    try:
        data = request.get_json()
        agent_id = data.get('agentId')
        scenario = data.get('scenario')

        # Fetch agent from database
        agent = Agent.query.get(agent_id)
        if not agent:
            return jsonify({'error': 'Agent not found'}), 404

        # Initialize Anthropic client with agent's API key
        client = anthropic.Anthropic(api_key=agent.api_key)

        # Create prompt for Gherkin generation
        prompt = f"""Convert the following manual scenario description into Cucumber Gherkin format.
Include: Feature, Scenario, Given, When, Then steps.

Scenario: {scenario}

Generate valid Gherkin syntax:"""

        # Call LLM
        message = client.messages.create(
            model=agent.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        gherkin_output = message.content[0].text

        return jsonify({'gherkin': gherkin_output})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
