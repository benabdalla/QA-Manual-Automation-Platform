{% extends "base.html" %}

{% block title %}Home - Ines QA Platform{% endblock %}

{% block content %}
<div class="home-container">
    <div class="container mt-5">
        <!-- Header Section -->
        <div class="home-header mb-5">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1 class="home-title mb-2">
                        <i class="fas fa-home"></i> Welcome, {{ user.username }}!
                    </h1>
                    <p class="home-subtitle text-muted">
                        <i class="fas fa-envelope"></i> {{ user.email }}
                    </p>
                </div>
                <div class="col-md-4 text-end">
                    <span class="badge bg-success me-2">
                        <i class="fas fa-check-circle"></i> Active
                    </span>
                    <a href="{{ url_for('auth.profile') }}" class="btn btn-outline-primary btn-sm">
                        <i class="fas fa-user-cog"></i> Profile
                    </a>
                </div>
            </div>
        </div>
        
        <!-- Stats Row -->
        <div class="row mb-4">
            <div class="col-md-3 mb-3">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-cogs"></i>
                    </div>
                    <div class="stat-content">
                        <h6>Agent Configs</h6>
                        <h3>{{ agent_configs }}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-browser"></i>
                    </div>
                    <div class="stat-content">
                        <h6>Browser Configs</h6>
                        <h3>{{ browser_configs }}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-calendar"></i>
                    </div>
                    <div class="stat-content">
                        <h6>Member Since</h6>
                        <h3 class="small">{{ user.created_at.strftime('%b %Y') }}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-rocket"></i>
                    </div>
                    <div class="stat-content">
                        <h6>Platform</h6>
                        <h3 class="small">v1.0</h3>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Quick Access Section -->
        <div class="mb-5">
            <h2 class="section-title mb-4">
                <i class="fas fa-star"></i> Quick Access - Choose Your Tool
            </h2>
            
            <div class="row">
                <!-- Card 1: Test Case Generator -->
                <div class="col-lg-4 col-md-6 mb-4">
                    <div class="feature-card card-1">
                        <div class="card-top-bar"></div>
                        <div class="card-body">
                            <h5 class="card-title">
                                <i class="fas fa-clipboard-list"></i> Test Case Generator
                            </h5>
                            <p class="card-description">
                                Generate comprehensive test cases for your Jira issues using AI. 
                                Automatically create well-structured test scenarios with steps, 
                                expected results, and detailed descriptions.
                            </p>
                            <div class="card-stats">
                                <span class="stat">
                                    <i class="fas fa-hourglass-half"></i> 2-5 min
                                </span>
                                <span class="stat">
                                    <i class="fas fa-file-json"></i> JSON Output
                                </span>
                            </div>
                            <a href="{{ url_for('main.test_generator_index') }}" class="btn btn-primary btn-block mt-3">
                                <i class="fas fa-rocket"></i> Start Generator
                            </a>
                        </div>
                    </div>
                </div>
                
                <!-- Card 2: Test IA Agent -->
                <div class="col-lg-4 col-md-6 mb-4">
                    <div class="feature-card card-2">
                        <div class="card-top-bar"></div>
                        <div class="card-body">
                            <h5 class="card-title">
                                <i class="fas fa-robot"></i> Test IA Agent
                            </h5>
                            <p class="card-description">
                                Deploy intelligent AI agents to automate your testing workflows.
                                Control browsers, interact with web applications, and execute 
                                complex testing scenarios with natural language instructions.
                            </p>
                            <div class="card-stats">
                                <span class="stat">
                                    <i class="fas fa-infinity"></i> Variable
                                </span>
                                <span class="stat">
                                    <i class="fas fa-cogs"></i> Automation
                                </span>
                            </div>
                            <a href="{{ url_for('main.test_ia_agent') }}" class="btn btn-primary btn-block mt-3">
                                <i class="fas fa-bullseye"></i> Launch Agent
                            </a>
                        </div>
                    </div>
                </div>
                
                <!-- Card 3: Code Generator -->
                <div class="col-lg-4 col-md-6 mb-4">
                    <div class="feature-card card-3">
                        <div class="card-top-bar"></div>
                        <div class="card-body">
                            <h5 class="card-title">
                                <i class="fas fa-code"></i> Code Generator
                            </h5>
                            <p class="card-description">
                                Generate production-ready test code and automation scripts.
                                Create test implementations in multiple programming languages 
                                with proper structure, error handling, and best practices.
                            </p>
                            <div class="card-stats">
                                <span class="stat">
                                    <i class="fas fa-hourglass-half"></i> 1-3 min
                                </span>
                                <span class="stat">
                                    <i class="fas fa-file-code"></i> Multiple Formats
                                </span>
                            </div>
                            <a href="{{ url_for('main.code_generator') }}" class="btn btn-primary btn-block mt-3">
                                <i class="fas fa-wrench"></i> Generate Code
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Getting Started Section -->
        <div class="row mt-5">
            <div class="col-md-6 mb-4">
                <div class="info-card">
                    <h5>
                        <i class="fas fa-book"></i> Documentation
                    </h5>
                    <ul>
                        <li><a href="#"><i class="fas fa-arrow-right"></i> Quick Start Guide</a></li>
                        <li><a href="#"><i class="fas fa-arrow-right"></i> API Reference</a></li>
                        <li><a href="#"><i class="fas fa-arrow-right"></i> Examples & Tutorials</a></li>
                    </ul>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="info-card">
                    <h5>
                        <i class="fas fa-cog"></i> Settings & Account
                    </h5>
                    <ul>
                        <li><a href="{{ url_for('auth.profile') }}"><i class="fas fa-arrow-right"></i> Profile Settings</a></li>
                        <li><a href="{{ url_for('main.jira_xray_settings') }}"><i class="fas fa-arrow-right"></i> Jira-Xray Settings</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_css %}
<style>
    .home-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
        padding: 40px 0;
    }
    
    .home-header {
        background: white;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #667eea;
    }
    
    .home-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1a202c;
        margin: 0;
    }
    
    .home-subtitle {
        font-size: 0.95rem;
        margin: 0;
    }
    
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        gap: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
    }
    
    .stat-icon {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.5rem;
    }
    
    .stat-content h6 {
        color: #999;
        font-size: 0.8rem;
        text-transform: uppercase;
        margin: 0 0 5px 0;
    }
    
    .stat-content h3 {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a202c;
        margin: 0;
    }
    
    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a202c;
    }
    
    .feature-card {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
    }
    
    .card-top-bar {
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .card-1 .card-top-bar {
        background: linear-gradient(90deg, #667eea, #60a5fa);
    }
    
    .card-2 .card-top-bar {
        background: linear-gradient(90deg, #764ba2, #a78bfa);
    }
    
    .card-3 .card-top-bar {
        background: linear-gradient(90deg, #ec4899, #f472b6);
    }
    
    .card-body {
        padding: 25px;
    }
    
    .card-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1a202c;
        margin-bottom: 15px;
    }
    
    .card-description {
        color: #666;
        font-size: 0.9rem;
        line-height: 1.6;
        margin-bottom: 15px;
    }
    
    .card-stats {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }
    
    .card-stats .stat {
        font-size: 0.85rem;
        background: #f0f4ff;
        color: #667eea;
        padding: 5px 10px;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    
    .btn-block {
        width: 100%;
    }
    
    .info-card {
        background: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    .info-card h5 {
        font-weight: 600;
        color: #1a202c;
        margin-bottom: 15px;
    }
    
    .info-card ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .info-card li {
        margin-bottom: 10px;
    }
    
    .info-card a {
        color: #667eea;
        text-decoration: none;
        transition: all 0.3s ease;
    }
    
    .info-card a:hover {
        color: #764ba2;
        margin-left: 5px;
    }
</style>
{% endblock %}

@main.route('/agent-gherkin-generator', methods=['GET'])
@login_required
def agent_gherkin_generator():
    """Display agent-based Gherkin generator interface"""
    from flask_app.models import Agent  # Adjust import based on your model location
    agents = Agent.query.filter_by(user_id=current_user.id).all()
    return render_template('main/agent_gherkin_generator.html', agents=agents)

@main.route('/generate-agent-gherkin', methods=['POST'])
@login_required
def generate_agent_gherkin():
    """Generate Gherkin scenarios using selected agent"""
    import json
    from flask_app.models import Agent
    
    agent_id = request.form.get('agent_id')
    feature_name = request.form.get('feature_name')
    scenario_description = request.form.get('scenario_description')
    scenario_count = request.form.get('scenario_count', 1)
    
    agent = Agent.query.filter_by(id=agent_id, user_id=current_user.id).first()
    
    if not agent:
        return jsonify({'error': 'Agent not found'}), 404
    
    try:
        # Call your LLM/Agent service to generate Gherkin scenarios
        gherkin_scenarios = generate_gherkin_with_agent(
            agent=agent,
            feature_name=feature_name,
            description=scenario_description,
            count=int(scenario_count)
        )
        
        return jsonify({
            'success': True,
            'scenarios': gherkin_scenarios
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_gherkin_with_agent(agent, feature_name, description, count):
    """Helper function to generate Gherkin using agent"""
    # Implement your LLM call here with agent's model and API
    # This should use agent.llm_model and agent.api_key
    # Return generated Gherkin scenarios
    pass