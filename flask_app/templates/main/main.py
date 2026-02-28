"""
Main Routes for Flask App
"""
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import text

from flask_app import db
from flask_app.app import app
from flask_app.models import SavedConfig, JiraXraySettings
import os

import requests
from requests.auth import HTTPBasicAuth
import json
import google.generativeai as genai
from flask import Flask, render_template, request, redirect, url_for, app, jsonify

import argparse

from flask_app.templates.utils.getxraytoken import file

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

    # Get user's saved configs count
    agent_configs_count = SavedConfig.query.filter_by(
        user_id=current_user.id,
        config_type='agent'
    ).count()

    browser_configs_count = SavedConfig.query.filter_by(
        user_id=current_user.id,
        config_type='browser'
    ).count()

    return render_template('main/home.html',
                          user=user_data,
                          agent_configs=agent_configs_count,
                          browser_configs=browser_configs_count)


@main_bp.route('/agent-settings')
@login_required
def agent_settings():
    """Agent settings tab"""
    configs = SavedConfig.query.filter_by(
        user_id=current_user.id,
        config_type='agent'
    ).all()
    return render_template('main/agent_settings.html', configs=configs)


@main_bp.route('/browser-settings')
@login_required
def browser_settings():
    """Browser settings tab"""
    configs = SavedConfig.query.filter_by(
        user_id=current_user.id,
        config_type='browser'
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
        index_generate()
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
    agents = SavedConfig.query.filter_by(
        user_id=current_user.id,
        config_type='agent'
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
        agent = SavedConfig.query.filter_by(
            id=agent_id,
            user_id=current_user.id,
            config_type='agent'
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



OPENAI_TOKEN_FILE = 'openai_token.txt'  # https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key
AI_MODEL = "gemini-2.0-flash"  # "gpt-3.5-turbo"

# Jira Cloud configuration
JIRA_TOKEN_FILE = 'jira_token.txt'  # https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/

# Jira Cloud API endpoint for creating issues (test cases)
XRAY_URL = "https://xray.cloud.getxray.app/api/v2/import/test/bulk"
XRAY_AUTH_JSON = 'xray_auth.json'  # File containing your XRAY API token https://community.atlassian.com/t5/Jira-Software-questions/Where-to-create-Xray-api-key/qaq-p/1923024

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        req = request.form["req"]
        username = request.form["username"]
        baseurl = request.form["baseurl"]
        project_key = request.form["project_key"]
        version_name = request.form["version_name"]
        folder_path = request.form["folder_path"]
        tc_amount = int(request.form.get("tc_amount", 1))
        skip_checks = "skip_checks" in request.form
        del_tc = "del_tc" in request.form
        debug = "debug" in request.form

        try:
            res=main(req, username, baseurl, project_key, version_name, folder_path, tc_amount, skip_checks, del_tc, debug)
            return redirect(url_for('resultat'))
        except Exception as e:
            result = f"❌ Une erreur est survenue : {e}"
            return render_template("index.html", result=result)

    return render_template("index.html", result=result)


@main_bp.route('/api/jira-xray-settings', methods=['GET'])
@login_required
def api_get_jira_xray_settings():
    """API endpoint to return current user's Jira/Xray settings as JSON"""
    settings = JiraXraySettings.get_user_jira_settings(current_user.id)

    if not settings:
        return jsonify({
            "success": False,
            "message": "Aucun paramètre trouvé pour cet utilisateur."
        }), 404

    return jsonify({
        "success": True,
        "data": {
            "jira_requirement_key": settings.get("jira_requirement_key", ""),
            "jira_username": settings.get("jira_username", ""),
            "jira_url": settings.get("jira_url", ""),
            "project_key": settings.get("project_key", ""),
            "version_name": settings.get("version_name", ""),
            "xray_folder_path": settings.get("xray_folder_path", ""),
            "num_test_cases": settings.get("num_test_cases", 1),
            "xray_client_id": settings.get("xray_client_id", ""),
            "xray_client_secret": settings.get("xray_client_secret", ""),
        }
    })
# Fetch Requirement Issue data
def get_issue_data(issue_key, BASE_URL, USERNAME):
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


# Define Test Case Issue
def delete_test_case(issue_key, BASE_URL, USERNAME):
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
    lines = raw_text.strip().splitlines()
    # Supprimer la première et la dernière ligne
    cleaned_lines = lines[1:-1]
    return "\n".join(cleaned_lines)


def generate_with_openai(prompt,project_key,version_name,folder_path,tc_amount,skip_checks=False,debug=True):
    with open(OPENAI_TOKEN_FILE, 'r') as file:
        genai.configure(api_key=file.readline().strip())
    # Create Prompt for Gemini
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
    # Combine system prompt and user prompt
    full_prompt = system_prompt + "\n\nSpécification des exigences :\n" + prompt
    try:
        response = model.generate_content(full_prompt)
        json_result = response.text.strip()
    except Exception as e:
        print(f"❌ Erreur lors de l'appel API: {e}")
        return None
    # Debug raw output
    if debug:
        print("Raw API response:", json_result)
    # Extract and parse JSON
    # json_result = json.loads(raw_output)
    json_result=clean_api_response(json_result)
    if json_result is None:
        print("❌ Failed to parse JSON from response")
        return None
    if debug:
        print("Parsed JSON:", json_result)
        print("✅ Generation Done.")
    # Filter test cases if needed
    # if not skip_checks:
    #     filtered_json_output = filter_test_cases(json_result)
    # else:
    filtered_json_output = json_result
    # Save to file
    with open('static/data/output_tc.json', 'w', encoding='utf-8') as file:
        json.dump(filtered_json_output, file, indent=2, ensure_ascii=False)
    return filtered_json_output

def import_test_cases_to_xray():
    # get XRAY token
    url = "https://xray.cloud.getxray.app/api/v2/authenticate"
    headers = {
        "Content-Type": "application/json"
    }
    with open(XRAY_AUTH_JSON, "r") as file:
        data = file.read()
    response = requests.post(url, headers=headers, data=data)
    # Removing double quotes from the response
    API_TOKEN = response.text.replace('"', '')
    AUTH = (API_TOKEN)
    # Open the file for reading
    with open('static/data/output_tc.json', 'r', encoding='utf-8') as f:
        content = f.read()
     # //   print("Contenu brut du fichier:", type(content))
     #    print(content)
    data = json.loads(content)
    if not isinstance(data, list):
        raise ValueError("The JSON structure is not as expected.")
    # for testcase in data:
    #     testcase['fields']['project'] = json.loads(
    #         '{ "key": "' + JIRA_PARENT_ISSUE.split("-")[0] + '" }')  # "project": { "key": "TSX" }
    #     testcase['update'] = json.loads(
    #         '{ "issuelinks": [ { "add": { "type": { "name": "Test" }, "outwardIssue": { "key": "' + JIRA_PARENT_ISSUE + '" } } } ] }')
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + AUTH
    }
    response = requests.post(XRAY_URL, headers=headers, data=json.dumps(data))
    # Check for successful request
    if response.status_code == 200 or response.status_code == 201:
        print("Test cases imported successfully!")
        print(response.json())
    else:
        print(f"Failed to import test cases. Status code: {response.status_code}")
        print(response.text)
        print(data)


def main(req, username, baseurl,project_key,version_name,folder_path, tc_amount, skip_checks, del_tc, debug):
    url = baseurl + '/rest/api/2'
    resultatJson= "";
    issue_data = get_issue_data(req, url, username)
    if issue_data:
        summ = "Requirement summary: " + issue_data['fields']['summary']
        # Check if issue type is requirement i.e. not type of 'Test', 'Test Set' or 'Test Plan'
        issueType = str(issue_data['fields']['issuetype']['name'])
        print("Issue type: " + issueType)
        if issueType == "Test" or issueType == "Test Set" or issueType == "Test Plan":
            print("Issue type is not a requirement. You cannot create linked Test Case for a Test item. Exiting.")
            # exit()
        # Check if issue has description
        if issue_data['fields']['description']:
            desc = "Requirement description: " + issue_data['fields']['description']
        else:
            desc = " "
            print("No Description using summary only!")
        req_data = summ + "\n" + desc
        print("Req data found:" + req + "\n" + req_data, flush=True)
    else:
        print("No love. Issue not found for id: " + req)
        # exit()
    # Check does issue have linked Test Cases
    if del_tc and issue_data['fields']['issuelinks']:
        # Loop through all linked issues
        for issue in issue_data['fields']['issuelinks']:
            # Check if linked issue is of type 'Test'
            if issue['type']['name'] == "Test":
                delete_test_case(issue['inwardIssue']['key'], url, username)
                print("Deleted linked Test Case: " + issue['inwardIssue']['key'], flush=True)
    # if skip_checks:
    #     print("Skipping checks.")
    #     generate_with_openai(req_data,project_key,version_name,folder_path, tc_amount, skip_checks)
    #     # import_test_cases_to_xray(req, debug)
    # else:
    #     # if input("Generate Test Cases: [y]/n?") != "n":
    resultatJson=generate_with_openai(req_data,project_key,version_name,folder_path, tc_amount, skip_checks)
        # import_test_cases_to_xray(req, debug)
    return  resultatJson




@main_bp.route('/resultat')
@login_required
def resultat():
    json_file_path = os.path.join(app.root_path, 'static', 'data', 'output_tc.json')

    if not os.path.exists(json_file_path):
        return jsonify({"error": "Fichier JSON non trouvé."}), 404

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Erreur de parsing JSON : {str(e)}"}), 400

    # ⚠️ Choisis soit JSON, soit HTML, mais pas les deux en même temps.
    # return jsonify(data)
    return render_template('resultat.html', testcases=data)  # On injecte data dans le template

# let testCases = JSON.parse('{{ result_json|safe }}');
# @main_bp.route("/", methods=["GET", "POST"])
# @login_required
# def index():
#     JiraXraySettings.get_user_jira_settings(5)
#     result = None
#     if request.method == "POST":
#         req = request.form["req"]
#
#
#         try:
#             username = request.form["username"]
#             baseurl = request.form["baseurl"]
#             project_key = request.form["project_key"]
#             version_name = request.form["version_name"]
#             folder_path = request.form["folder_path"]
#             tc_amount = int(request.form.get("tc_amount", 1))
#             skip_checks = "skip_checks" in request.form
#             del_tc = "del_tc" in request.form
#             debug = "debug" in request.form
#             res=main(req, username, baseurl, project_key, version_name, folder_path, tc_amount, skip_checks, del_tc, debug)
#             return redirect(url_for('resultat'))
#         except Exception as e:
#             result = f"❌ Une erreur est survenue : {e}"
#             return render_template("index.html", result=result)
#
#     return render_template("index.html", result=result)

def index_generate():
    result = None

    # ✅ Get current logged-in user from Flask-Login session
    user_id = current_user.id

    # ✅ Load saved settings from DB for this user
    settings = JiraXraySettings.get_user_jira_settings(user_id)

    if request.method == "POST":
        input_source = request.form.get("input_source", "jira_key")

        # ✅ Form value OR fallback to DB setting
        username     =(settings.get("jira_username")     if settings else "")
        baseurl      = (settings.get("jira_url")          if settings else "")
        project_key  =(settings.get("project_key")       if settings else "")
        version_name = (settings.get("version_name")      if settings else "")
        folder_path  =(settings.get("xray_folder_path")  if settings else "")
        tc_amount    = int(request.form.get("tc_amount") or (settings.get("num_test_cases", 1) if settings else 1))
        skip_checks  = "skip_checks" in request.form
        del_tc       = "del_tc"       in request.form
        debug        = "debug"        in request.form

        # ✅ Handle input source: Jira key vs User Story
        if input_source == "user_story":
            req        = None
            user_story = request.form.get("user_story", "").strip()
            if not user_story:
                result = "❌ Veuillez saisir une user story."
                return render_template("index.html", result=result, settings=settings)
        else:
            req        = request.form.get("req", "").strip() or (settings.get("jira_requirement_key") if settings else "")
            user_story = None
            if not req:
                result = "❌ Veuillez saisir une clé de requirement."
                return render_template("index.html", result=result, settings=settings)

        try:
            main(
                req, username, baseurl, project_key, version_name,
                folder_path, tc_amount, skip_checks, del_tc, debug,
                user_story=user_story
            )
            return redirect(url_for('main_bp.resultat'))
        except Exception as e:
            result = f"❌ Une erreur est survenue : {e}"
            return render_template("index.html", result=result, settings=settings)

    return render_template("index.html", result=result, settings=settings)


@main_bp.route('/save_tests', methods=['POST'])
@login_required
def save_tests():
    json_file_path = os.path.join(app.root_path, 'static', 'data', 'output_tc.json')
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({"error": "Les données doivent être une liste."}), 400

        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return jsonify({"message": "✅ Données sauvegardées avec succès."})
    except Exception as e:
        return jsonify({"error": f"Erreur lors de l'enregistrement : {str(e)}"}), 500



@main_bp.route('/import-xray', methods=['POST'])
@login_required
def import_xray():
    try:
        # Simule une importation
        import_test_cases_to_xray()
        print("import_test_cases_to_xray called")
        return render_template("index.html", result="data insert.")
    except Exception as e:
        print(f"Erreur Xray: {e}")
        return redirect(url_for('resultat'))




def _mask(val):
    if not val or len(val) < 8:
        return '••••••••'
    return val[:6] + '•••••••' + val[-4:]


# GET /api/api-keys
@main_bp.route('/api/api-keys', methods=['GET'])
@login_required
def get_api_keys():
    try:
        result = db.session.execute(text("""
            SELECT id, user_id, key_name, key_value, key_type, is_active, created_at, last_used
            FROM api_keys WHERE user_id = :uid ORDER BY created_at DESC
        """), {"uid": current_user.id})

        keys = []
        for row in result.fetchall():
            d = dict(row._mapping)
            d['key_value']  = _mask(d['key_value'])
            d['created_at'] = d['created_at'].isoformat() if d['created_at'] else None
            d['last_used']  = d['last_used'].isoformat()  if d['last_used']  else None
            keys.append(d)

        return jsonify({"success": True, "keys": keys}), 200
    except Exception as e:
        print(f"❌ GET api_keys error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# POST /api/api-keys
@main_bp.route('/api/api-keys-xray', methods=['POST'])
@login_required
def create_api_key():
    print("🔥 ROUTE HIT - create_api_key")

    body = request.get_json(force=True, silent=True)
    print(f"BODY: {body}")

    if not body:
        return jsonify({"success": False, "error": "Cannot parse request body"}), 400

    key_name  = str(body.get('key_name')  or '').strip()
    key_type  = str(body.get('key_type')  or '').strip()
    key_value = str(body.get('key_value') or '').strip()
    raw       = body.get('is_active', True)
    is_active = raw if isinstance(raw, bool) else str(raw).lower() not in ('false', '0', 'no', '')

    print(f"→ name='{key_name}' type='{key_type}' value='{key_value}' active={is_active}")

    if not key_name:  return jsonify({"success": False, "error": "key_name is required"}), 400
    if not key_type:  return jsonify({"success": False, "error": "key_type is required"}), 400
    if not key_value: return jsonify({"success": False, "error": "key_value is required"}), 400

    try:
        result = db.session.execute(text("""
            INSERT INTO api_keys (user_id, key_name, key_value, key_type, is_active, created_at)
            VALUES (:user_id, :key_name, :key_value, :key_type, :is_active, :now)
            RETURNING id
        """), {
            "user_id":  current_user.id,   # ✅ no space
            "key_name":  key_name,
            "key_value": key_value,
            "key_type":  key_type,
            "is_active": is_active,
            "now":       datetime.utcnow()  # ✅ created_at provided
        })
        db.session.commit()
        new_id = result.fetchone()[0]
        print(f"✅ KEY CREATED id={new_id}")
        return jsonify({"success": True, "message": "API key created", "id": new_id}), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ DB ERROR: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# PUT /api/api-keys/<id>
@main_bp.route('/api/api-keys/<int:key_id>', methods=['PUT'])
@login_required
def update_api_key(key_id):
    try:
        check = db.session.execute(
            text("SELECT id FROM api_keys WHERE id = :id AND user_id = :uid"),
            {"id": key_id, "uid": current_user.id}
        ).fetchone()
        if not check:
            return jsonify({"success": False, "error": "Key not found or access denied"}), 404

        body      = request.get_json()
        key_name  = (body.get('key_name') or '').strip()
        key_type  = (body.get('key_type') or '').strip()
        is_active = bool(body.get('is_active', True))
        new_value = (body.get('key_value') or '').strip()

        if new_value:
            db.session.execute(text("""
                UPDATE api_keys SET key_name=:n, key_type=:t, key_value=:v, is_active=:a
                WHERE id=:id AND user_id=:uid
            """), {"n": key_name, "t": key_type, "v": new_value, "a": is_active,
                   "id": key_id, "uid": current_user.id})
        else:
            db.session.execute(text("""
                UPDATE api_keys SET key_name=:n, key_type=:t, is_active=:a
                WHERE id=:id AND user_id=:uid
            """), {"n": key_name, "t": key_type, "a": is_active,
                   "id": key_id, "uid": current_user.id})

        db.session.commit()
        return jsonify({"success": True, "message": "Key updated"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# DELETE /api/api-keys/<id>
@app.route('/api/api-keys/<int:key_id>', methods=['DELETE'])
@login_required
def delete_api_key(key_id):
    try:
        check = db.session.execute(
            text("SELECT id FROM api_keys WHERE id = :id AND user_id = :uid"),
            {"id": key_id, "uid": current_user.id}
        ).fetchone()
        if not check:
            return jsonify({"success": False, "error": "Key not found or access denied"}), 404

        db.session.execute(
            text("DELETE FROM api_keys WHERE id = :id AND user_id = :uid"),
            {"id": key_id, "uid": current_user.id}
        )
        db.session.commit()
        return jsonify({"success": True, "message": "Key deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# GET /api/api-keys/by-type/<type>  — internal use to retrieve actual key value
@main_bp.route('/api/api-keys/by-type/<string:key_type>', methods=['GET'])
@login_required
def get_key_by_type(key_type):
    try:
        row = db.session.execute(text("""
            SELECT id, key_name, key_value FROM api_keys
            WHERE user_id=:uid AND key_type=:t AND is_active=TRUE
            ORDER BY created_at DESC LIMIT 1
        """), {"uid": current_user.id, "t": key_type}).fetchone()

        if not row:
            return jsonify({"success": False, "error": f"No active {key_type} key found"}), 404

        db.session.execute(
            text("UPDATE api_keys SET last_used=:now WHERE id=:id"),
            {"now": datetime.utcnow(), "id": row.id}
        )
        db.session.commit()

        return jsonify({"success": True, "id": row.id,
                        "key_name": row.key_name,
                        "key_value": row.key_value}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# GET /api/api-keys/history
@main_bp.route('/api/api-keys/history', methods=['GET'])
@login_required
def get_keys_history():
    try:
        rows = db.session.execute(text("""
            SELECT key_name, key_type, created_at, last_used
            FROM api_keys WHERE user_id=:uid
            ORDER BY COALESCE(last_used, created_at) DESC LIMIT 20
        """), {"uid": current_user.id}).fetchall()

        history = []
        for row in rows:
            d = dict(row._mapping)
            if d['last_used']:
                history.append({"timestamp": d['last_used'].isoformat(),
                                 "action": "used", "key_name": d['key_name'],
                                 "details": d['key_type']})
            history.append({"timestamp": d['created_at'].isoformat(),
                             "action": "created", "key_name": d['key_name'],
                             "details": d['key_type']})

        history.sort(key=lambda x: x['timestamp'], reverse=True)
        return jsonify({"success": True, "history": history[:20]}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500