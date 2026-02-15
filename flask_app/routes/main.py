"""
Main Routes for Flask App
"""
from flask import Blueprint, render_template, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from flask_app.models import AgentSettings, JiraXraySettings
from flask_app import db
from datetime import datetime
import os
import json
import requests
from requests.auth import HTTPBasicAuth
import google.generativeai as genai

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home redirect"""
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return redirect(url_for('auth.login'))


@main_bp.route('/home')
@login_required
def home():
    """Home page after login"""
    user_data = {
        'username': current_user.username,
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'avatar': current_user.avatar,
        'created_at': current_user.created_at
    }
    
    # Get user's agent settings count
    agent_configs_count = AgentSettings.query.filter_by(
        user_id=current_user.id, 
    ).count()
    
    # Remove config_type filter, as agent_settings has no such column
    browser_configs_count = AgentSettings.query.filter_by(
        user_id=current_user.id
    ).count()
    
    return render_template('main/home.html', 
                          user=user_data,
                          agent_configs=agent_configs_count,
                          browser_configs=browser_configs_count)


@main_bp.route('/agent-settings')
@login_required
def agent_settings():
    """Agent settings tab"""
    configs = AgentSettings.query.filter_by(
        user_id=current_user.id
    ).all()
    return render_template('main/agent_settings.html', configs=configs)


@main_bp.route('/browser-settings')
@login_required
def browser_settings():
    """Browser settings tab"""
    # Remove config_type filter, as agent_settings has no such column
    configs = AgentSettings.query.filter_by(
        user_id=current_user.id
    ).all()
    return render_template('main/browser_settings.html', configs=configs)


@main_bp.route('/api-keys')
@login_required
def api_keys_management():
    """API Keys management page"""
    return render_template('main/api_keys.html')


@main_bp.route('/model-settings')
@login_required
def model_settings():
    """Model and API configuration settings page"""
    return render_template('main/model_settings.html', user=current_user)


@main_bp.route('/run-agent', endpoint='main_run_agent')
@login_required
def run_agent():
    """Run agent tab"""
    return render_template('main/run_agent.html')


@main_bp.route('/test-generator-index', methods=['GET', 'POST'])
@login_required
def test_generator_index():
    """Test generator index page"""
    # Handle POST requests by redirecting to GET
    if request.method == 'POST':
        return redirect(url_for('main.test_generator_index'))
    return render_template('main/index.html')


@main_bp.route('/test-case-generator', methods=['GET', 'POST'])
@login_required
def test_case_generator():
    """Test case generator page"""
    # Handle POST requests by redirecting to GET
    if request.method == 'POST':
        return redirect(url_for('main.test_case_generator'))
    return render_template('main/test_case_generator.html')


@main_bp.route('/test-ia-agent')
@login_required
def test_ia_agent():
    """Test IA Agent page"""
    return render_template('main/test_ia_agent.html')


@main_bp.route('/code-generator')
@login_required
def code_generator():
    """Code generator page"""
    return render_template('main/code_generator.html')


@main_bp.route('/agent-gherkin-generator')
@login_required
def agent_gherkin_generator():
    """Agent Gherkin generator page"""
    # Fetch agents from database for current user
    agents = AgentSettings.query.filter_by(
        user_id=current_user.id
    ).all()
    return render_template('main/agent_gherkin_generator.html', agents=agents)


@main_bp.route('/agent-gherkin-generator/generate', methods=['POST'])
@login_required
def generate_agent_gherkin():
    """Generate gherkin scenarios using selected agent"""
    try:
        agent_id = request.form.get("agent_id")
        feature_name = request.form.get("feature_name")
        scenario_description = request.form.get("scenario_description")
        scenario_count = int(request.form.get("scenario_count", 1))
        
        # Fetch agent configuration
        agent = AgentSettings.query.filter_by(
            id=agent_id,
            user_id=current_user.id
        ).first()
        
        if not agent:
            return jsonify({"error": "Agent not found"}), 404
        
        # Build prompt for gherkin generation
        system_prompt = (
            f"You are a BDD test scenario expert. Generate {scenario_count} Gherkin scenario(s) "
            f"for the feature '{feature_name}'. "
            "The response must be valid Gherkin format (Given/When/Then) without any additional text.\n\n"
            "Format:\n"
            "Feature: Feature Name\n"
            "  Scenario: Scenario Name\n"
            "    Given [precondition]\n"
            "    When [action]\n"
            "    Then [expected result]"
        )
        
        full_prompt = system_prompt + "\n\nFeature Description:\n" + scenario_description
        
        # Call generative AI to generate gherkin
        genai.configure(api_key=file.readline().strip())
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        try:
            response = model.generate_content(full_prompt)
            gherkin_result = response.text.strip()
        except Exception as e:
            return jsonify({"error": f"Failed to generate scenarios: {str(e)}"}), 500
        
        return jsonify({
            "message": "Gherkin scenarios generated successfully!",
            "gherkin": gherkin_result,
            "feature_name": feature_name,
            "scenario_count": scenario_count
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_bp.route('/jira-xray-settings')
@login_required
def jira_xray_settings():
    """Jira-Xray settings configuration page"""
    settings = JiraXraySettings.query.filter_by(user_id=current_user.id).all()
    return render_template('main/jira_xray_settings.html', settings=settings)


@main_bp.route('/resultat')
@login_required
def resultat():
    """Display generated test cases results"""
    json_file_path = os.path.join(current_app.root_path, 'static', 'data', 'output_tc.json')

    if not os.path.exists(json_file_path):
        return render_template('main/resultat.html', testcases=[], error='No test cases found. Please generate test cases first.')

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return render_template('main/resultat.html', testcases=[], error=f'Error parsing test cases: {str(e)}')

    return render_template('main/resultat.html', testcases=data)


# Configuration for test case generation
OPENAI_TOKEN_FILE = 'openai_token.txt'
JIRA_TOKEN_FILE = 'jira_token.txt'
XRAY_URL = "https://xray.cloud.getxray.app/api/v2/import/test/bulk"
XRAY_AUTH_JSON = 'xray_auth.json'


def get_issue_data(issue_key, BASE_URL, USERNAME):
    """Fetch Requirement Issue data from Jira"""
    with open(JIRA_TOKEN_FILE, 'r') as file:
        JIRA_TOKEN = file.readline().strip()
    url = f"{BASE_URL}/issue/{issue_key}"

    headers = {
        'Accept': 'application/json',
    }

    response = requests.get(
        url,
        headers=headers,
        auth=HTTPBasicAuth(USERNAME, JIRA_TOKEN)
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch issue data. Status code: {response.status_code}")
        print(response.text)
        return None


def delete_test_case(issue_key, BASE_URL, USERNAME):
    """Delete Test Case from Jira"""
    with open(JIRA_TOKEN_FILE, 'r') as file:
        JIRA_TOKEN = file.readline().strip()
    url = f"{BASE_URL}/issue/{issue_key}"

    headers = {
        'Accept': 'application/json',
    }

    response = requests.delete(
        url,
        headers=headers,
        auth=HTTPBasicAuth(USERNAME, JIRA_TOKEN)
    )

    if response.status_code == 204:
        print("Test Case deleted successfully!")
    else:
        print(f"Failed to delete Test Case. Status code: {response.status_code}")
        print(response.text)
        return None


def clean_api_response(raw_text):
    """Clean API response by removing first and last lines"""
    lines = raw_text.strip().splitlines()
    cleaned_lines = lines[1:-1]
    return "\n".join(cleaned_lines)


def generate_with_openai(prompt, project_key, version_name, folder_path, tc_amount, skip_checks=False, debug=True, app=None):
    """Generate test cases using Google Generative AI"""
    with open(OPENAI_TOKEN_FILE, 'r') as file:
        genai.configure(api_key=file.readline().strip())
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    system_prompt = (
        f"Générer cas de test pour la spécification des exigences fournie, en français. "
        "La réponse doit être uniquement au format JSON valide, sans texte supplémentaire ni markdown.\n\n"
        "Format JSON à utiliser :\n"
        '[\n'
        '    {\n'
        '        "testtype": "Manual",\n'
        '        "fields": {\n'
        f'            "project": {{ "key": "{project_key}" }},\n'
        f'            "fixVersions": [{{ "name": "{version_name}" }}],\n'
        '            "summary": "Cas de test 1 : Test de vitesse minimale",\n'
        '            "description": "Objectif : Vérifier que...\\nPréconditions : ..."\n'
        '        },\n'
        '        "steps": [\n'
        '            {\n'
        '                "action": "Démarrer une récupération de données vers ...",\n'
        '                "data": "",\n'
        '                "result": "L\'opération de récupération de données doit être terminée..."\n'
        '            }\n'
        '        ],'
        f'        "xray_test_repository_folder": "{folder_path}"\n'
        '    }\n'
        ']'
    )
    
    full_prompt = system_prompt + "\n\nSpécification des exigences :\n" + prompt
    
    try:
        response = model.generate_content(full_prompt)
        json_result = response.text.strip()
    except Exception as e:
        print(f"❌ Erreur lors de l'appel API: {e}")
        return None
    
    if debug:
        print("Raw API response:", json_result)
    
    json_result = clean_api_response(json_result)
    if json_result is None:
        print("❌ Failed to parse JSON from response")
        return None
    
    try:
        json_data = json.loads(json_result)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {e}")
        return None
    
    if debug:
        print("Parsed JSON:", json_result)
        print("✅ Generation Done.")
    
    filtered_json_output = json_data
    
    # Save to file with proper path resolution
    if app:
        json_file_path = os.path.join(app.root_path, 'static', 'data', 'output_tc.json')
    else:
        json_file_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'data', 'output_tc.json')
    
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
    
    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(filtered_json_output, file, indent=2, ensure_ascii=False)
    
    return filtered_json_output


def generate_test_cases_main(req, username, baseurl, project_key, version_name, folder_path, tc_amount, skip_checks, del_tc, debug):
    """Main function to generate test cases from Jira requirement"""
    url = baseurl + '/rest/api/2'
    issue_data = get_issue_data(req, url, username)
    
    if issue_data:
        summ = "Requirement summary: " + issue_data['fields']['summary']
        issueType = str(issue_data['fields']['issuetype']['name'])
        print("Issue type: " + issueType)
        
        if issueType == "Test" or issueType == "Test Set" or issueType == "Test Plan":
            print("Issue type is not a requirement. You cannot create linked Test Case for a Test item. Exiting.")
        
        if issue_data['fields']['description']:
            desc = "Requirement description: " + issue_data['fields']['description']
        else:
            desc = " "
            print("No Description using summary only!")
        
        req_data = summ + "\n" + desc
        print("Req data found:" + req + "\n" + req_data, flush=True)
    else:
        print("No love. Issue not found for id: " + req)
        return None
    
    if del_tc and issue_data['fields']['issuelinks']:
        for issue in issue_data['fields']['issuelinks']:
            if issue['type']['name'] == "Test":
                delete_test_case(issue['inwardIssue']['key'], url, username)
                print("Deleted linked Test Case: " + issue['inwardIssue']['key'], flush=True)
    
    resultatJson = generate_with_openai(req_data, project_key, version_name, folder_path, tc_amount, skip_checks, app=current_app)
    return resultatJson


@main_bp.route("/generate", methods=["GET", "POST"])
@login_required
def generate():
    """Generate test cases from form submission"""
    result = None
    if request.method == "POST":
        try:
            req = request.form.get("req")
            username = request.form.get("username")
            baseurl = request.form.get("baseurl")
            project_key = request.form.get("project_key")
            version_name = request.form.get("version_name")
            folder_path = request.form.get("folder_path")
            tc_amount = int(request.form.get("tc_amount", 1))
            skip_checks = "skip_checks" in request.form
            del_tc = "del_tc" in request.form
            debug = "debug" in request.form

            res = generate_test_cases_main(req, username, baseurl, project_key, version_name, folder_path, tc_amount, skip_checks, del_tc, debug)
            return redirect(url_for('main.resultat'))
        except Exception as e:
            result = f"❌ Une erreur est survenue : {e}"
            return render_template("main/index.html", result=result)

    return render_template("main/index.html", result=result)


@main_bp.route('/save_tests', methods=['POST'])
@login_required
def save_tests():
    """Save edited test cases back to JSON file"""
    json_file_path = os.path.join(current_app.root_path, 'static', 'data', 'output_tc.json')
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({"error": "Les donnees doivent etre une liste."}), 400

        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return jsonify({"message": "Donnees sauvegardees avec succes."})
    except Exception as e:
        return jsonify({"error": f"Erreur lors de l'enregistrement : {str(e)}"}), 500


def import_test_cases_to_xray():
    """Import generated test cases to Xray"""
    url = "https://xray.cloud.getxray.app/api/v2/authenticate"
    headers = {"Content-Type": "application/json"}
    with open(XRAY_AUTH_JSON, "r") as file:
        data = file.read()
    response = requests.post(url, headers=headers, data=data)
    API_TOKEN = response.text.replace('"', '')

    json_file_path = os.path.join(current_app.root_path, 'static', 'data', 'output_tc.json')
    with open(json_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    data = json.loads(content)
    if not isinstance(data, list):
        raise ValueError("The JSON structure is not as expected.")

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + API_TOKEN
    }
    response = requests.post(XRAY_URL, headers=headers, data=json.dumps(data))
    if response.status_code == 200 or response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Failed to import test cases. Status code: {response.status_code}")


@main_bp.route('/import-xray', methods=['POST'])
@login_required
def import_xray():
    """Import test cases to Xray"""
    try:
        result = import_test_cases_to_xray()
        return jsonify({"message": "Test cases imported successfully!", "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500