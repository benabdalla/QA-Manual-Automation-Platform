"""
Main Routes for Flask App
"""
import re
from functools import wraps
from pathlib import Path

from flask import Blueprint, render_template, redirect, session, url_for, request, jsonify, current_app, abort, \
    send_file
from flask_app.models import AgentSettings, JiraXraySettings, APIKey, User

import google.generativeai as genai
import os
import sys

from flask_app.routes.auth import send_welcome_email

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import text

from flask_app import db
from flask_app.models import SavedConfig, JiraXraySettings
import os

import requests
from requests.auth import HTTPBasicAuth
import json
from flask import Flask, render_template, request, redirect, url_for, app, jsonify

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



@main_bp.route("/api/me")
@login_required
def get_me():
    return jsonify({
        "user_id": current_user.id
    })

@main_bp.route('/test-ia-agent')
@login_required
def test_ia_agent():
    """Test IA Agent page"""
    
    return render_template('main/test_ia_agent.html', user_id=session.get("user_id"))


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
        result = APIKey.get_active_keys(user_id=current_user.id)
        genai.configure(api_key=result[0]["key_value"])
        model = genai.GenerativeModel(result[0]["key_type"])
        
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
XRAY_URL = "https://xray.cloud.getxray.app/api/v2/import/test/bulk"



def get_issue_data(issue_key, BASE_URL, USERNAME,jira_api_token):
    """Fetch Requirement Issue data from Jira"""
    url = f"{BASE_URL}/issue/{issue_key}"

    headers = {
        'Accept': 'application/json',
    }

    response = requests.get(
        url,
        headers=headers,
        auth=HTTPBasicAuth(USERNAME,jira_api_token)
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch issue data. Status code: {response.status_code}")
        print(response.text)
        return None


def delete_test_case(issue_key, BASE_URL, USERNAME,jira_api_token):
    """Delete Test Case from Jira"""
    url = f"{BASE_URL}/issue/{issue_key}"

    headers = {
        'Accept': 'application/json',
    }

    response = requests.delete(
        url,
        headers=headers,
        auth=HTTPBasicAuth(USERNAME, jira_api_token)
    )

    if response.status_code == 204:
        print("Test Case deleted successfully!")
    else:
        print(f"Failed to delete Test Case. Status code: {response.status_code}")
        print(response.text)
        return None


def clean_api_response(raw_text):
    """
    Extract valid JSON array from LLM response safely.
    Handles:
    - Extra text before/after JSON
    - Markdown ```json blocks
    - Trailing commas
    """

    if not raw_text:
        return None

    # Remove markdown blocks if present
    raw_text = re.sub(r"```json", "", raw_text, flags=re.IGNORECASE)
    raw_text = re.sub(r"```", "", raw_text)

    # Extract first JSON array
    match = re.search(r"\[.*\]", raw_text, re.DOTALL)
    if not match:
        return None

    json_text = match.group(0)

    # Remove trailing commas (common LLM mistake)
    json_text = re.sub(r",\s*}", "}", json_text)
    json_text = re.sub(r",\s*]", "]", json_text)

    # Remove BOM if exists
    json_text = json_text.encode().decode("utf-8-sig")

    return json_text.strip()


def generate_with_openai(prompt, project_key, version_name, folder_path,
                         tc_amount, skip_checks=False, debug=True, app=None):

    # 🔐 Get API key
    result = APIKey.get_active_keys(user_id=current_user.id)

    if not result:
        print("❌ No active API key found.")
        return None

    genai.configure(api_key=result[0]["key_value"])
    model = genai.GenerativeModel(result[0]["key_type"])

    system_prompt = f"""
Générer {tc_amount} cas de test pour la spécification fournie.
La réponse doit être UNIQUEMENT un JSON VALIDE.
Ne pas ajouter de texte, pas de markdown.

Format exact attendu :
[
  {{
    "testtype": "Manual",
    "fields": {{
      "project": {{ "key": "{project_key}" }},
      "fixVersions": [{{ "name": "{version_name}" }}],
      "summary": "Titre",
      "description": "Objectif...\\nPréconditions..."
    }},
    "steps": [
      {{
        "action": "Action",
        "data": "",
        "result": "Résultat attendu"
      }}
    ],
    "xray_test_repository_folder": "{folder_path}"
  }}
]
"""

    full_prompt = system_prompt + "\n\nSpécification :\n" + prompt

    try:
        response = model.generate_content(full_prompt)
        json_result = response.text.strip()
    except Exception as e:
        print(f"❌ API Error: {e}")
        return None

    if debug:
        print("Raw API response:")
        print(json_result)

    # 🔥 Clean safely
    json_result = clean_api_response(json_result)

    if not json_result:
        print("❌ No valid JSON detected.")
        return None

    try:
        json_data = json.loads(json_result)
    except json.JSONDecodeError as e:
        print("❌ JSON Decode Error:", e)
        print("Problematic JSON:")
        print(json_result)
        return None

    if debug:
        print("✅ JSON Parsed Successfully")

    # 📁 Save file
    if app:
        json_file_path = os.path.join(app.root_path, 'static', 'data', 'output_tc.json')
    else:
        json_file_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'data', 'output_tc.json')

    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, indent=2, ensure_ascii=False)

    return json_data

def generate_test_cases_main(req, username, baseurl, project_key, version_name, folder_path, tc_amount, skip_checks, del_tc, debug,jira_api_token):
    """Main function to generate test cases from Jira requirement"""
    url = baseurl + '/rest/api/2'
    issue_data = get_issue_data(req, url, username,jira_api_token)
    
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
                delete_test_case(issue['inwardIssue']['key'], url, username,jira_api_token)
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
            result= JiraXraySettings.get_user_credentials(user_id=current_user.id)
            print(result["jira_api_token"])
            result2=APIKey.get_active_keys(user_id=current_user.id)
            print(result2[0]["key_value"])
            print(result2[0]["key_type"])
            res = generate_test_cases_main(req, username, baseurl, project_key, version_name, folder_path, tc_amount, skip_checks, del_tc, debug,result["jira_api_token"])
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
    creds = JiraXraySettings.get_user_credentials(user_id=current_user.id)
    client_id = creds["xray_client_id"]
    client_secret = creds["xray_client_secret"]

    if not client_id or not client_secret:
        raise ValueError("Xray client ID or secret is missing. Please update your Jira/Xray settings.")

    # ✅ Build the auth payload directly from DB values (replaces xray_auth.json)
    auth_payload = json.dumps({
        "client_id": client_id,
        "client_secret": client_secret
    })
    response = requests.post(url, headers=headers, data=auth_payload)
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

    creds = JiraXraySettings.get_user_jira_xray_url(user_id=current_user.id)
    jira_url = creds["jira_url"].rstrip('/')  # remove trailing slash if any
    project_key = creds["project_key"]

    try:
        result = import_test_cases_to_xray()

        xray_url = (
            f"{jira_url}/projects/{project_key}"
            f"?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:"
            f"com.xpandit.plugins.xray__testing-board"
            f"#!page=test-repository"
        )

        return jsonify({
            "message": "Test cases imported successfully!",
            "result": result,
            "redirect_url": xray_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# API Keys CRUD
# ---------------------------------------------------------------------------
def _mask(val):
    if not val or len(val) < 8:
        return '••••••••'
    return val[:6] + '•••••••' + val[-4:]

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
        return jsonify({"success": False, "error": str(e)}), 500


@main_bp.route('/api/api-keys-xray', methods=['POST'])
@login_required
def create_api_key():
    body = request.get_json(force=True, silent=True)
    if not body:
        return jsonify({"success": False, "error": "Cannot parse request body"}), 400

    key_name  = str(body.get('key_name')  or '').strip()
    key_type  = str(body.get('key_type')  or '').strip()
    key_value = str(body.get('key_value') or '').strip()
    raw       = body.get('is_active', True)
    is_active = raw if isinstance(raw, bool) else str(raw).lower() not in ('false', '0', 'no', '')

    if not key_name:  return jsonify({"success": False, "error": "key_name is required"}), 400
    if not key_type:  return jsonify({"success": False, "error": "key_type is required"}), 400
    if not key_value: return jsonify({"success": False, "error": "key_value is required"}), 400

    try:
        # ✅ Use ORM insert — works on PostgreSQL, MySQL, and SQLite
        new_key = APIKey(
            user_id    = current_user.id,
            key_name   = key_name,
            key_value  = key_value,
            key_type   = key_type,
            is_active  = is_active,
            created_at = datetime.utcnow(),
            last_used = datetime.utcnow()



        )
        db.session.add(new_key)
        db.session.commit()          # ✅ commit first
        new_id = new_key.id          # ✅ read ID after commit (ORM populates it)

        return jsonify({
            "success": True,
            "message": "API key created",
            "id":      new_id
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"❌ create_api_key error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@main_bp.route('/api/api-keys/<int:key_id>', methods=['PUT'])
@login_required
def update_api_key(key_id):
    try:
        check = db.session.execute(
            text("SELECT id FROM api_keys WHERE id=:id AND user_id=:uid"),
            {"id": key_id, "uid": current_user.id}
        ).fetchone()
        if not check:
            return jsonify({"success": False, "error": "Key not found"}), 404
        body      = request.get_json()
        key_name  = (body.get('key_name')  or '').strip()
        key_type  = (body.get('key_type')  or '').strip()
        is_active = bool(body.get('is_active', True))
        new_value = (body.get('key_value') or '').strip()
        if new_value:
            db.session.execute(text(
                "UPDATE api_keys SET key_name=:n, key_type=:t, key_value=:v, is_active=:a "
                "WHERE id=:id AND user_id=:uid"
            ), {"n": key_name, "t": key_type, "v": new_value, "a": is_active,
                "id": key_id, "uid": current_user.id})
        else:
            db.session.execute(text(
                "UPDATE api_keys SET key_name=:n, key_type=:t, is_active=:a "
                "WHERE id=:id AND user_id=:uid"
            ), {"n": key_name, "t": key_type, "a": is_active,
                "id": key_id, "uid": current_user.id})
        db.session.commit()
        return jsonify({"success": True, "message": "Key updated"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@main_bp.route('/api/api-keys/<int:key_id>', methods=['DELETE'])
@login_required
def delete_api_key(key_id):
    try:
        check = db.session.execute(
            text("SELECT id FROM api_keys WHERE id=:id AND user_id=:uid"),
            {"id": key_id, "uid": current_user.id}
        ).fetchone()
        if not check:
            return jsonify({"success": False, "error": "Key not found"}), 404
        db.session.execute(
            text("DELETE FROM api_keys WHERE id=:id AND user_id=:uid"),
            {"id": key_id, "uid": current_user.id}
        )
        db.session.commit()
        return jsonify({"success": True, "message": "Key deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


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
                        "key_name": row.key_name, "key_value": row.key_value}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@main_bp.route('/api/api-keys/history', methods=['GET'])
@login_required
def get_keys_history():
    try:
        rows = db.session.execute(text("""
            SELECT key_name, key_type, created_at, last_used FROM api_keys
            WHERE user_id=:uid ORDER BY COALESCE(last_used, created_at) DESC LIMIT 20
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


# ── Admin guard decorator ─────────────────────────────────────────────────────
def admin_required(f):
    """Decorator: only allow users with is_admin=True."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ── Page route ────────────────────────────────────────────────────────────────
@main_bp.route('/admin/users')
@admin_required
def admin_users():
    """Render the admin user management page."""
    return render_template('main/admin_users.html')


# ── GET all users ─────────────────────────────────────────────────────────────
@main_bp.route('/api/admin/users', methods=['GET'])
@admin_required
def api_get_all_users():
    """Return all users as JSON."""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify({
            "success": True,
            "users": [
                {
                    "id":            u.id,
                    "username":      u.username,
                    "email":         u.email,
                    "first_name":    u.first_name  or "",
                    "last_name":     u.last_name   or "",
                    "avatar":        u.avatar      or "👤",
                    "is_active":     u.is_active,
                    "is_admin":      u.is_admin,
                    "created_at":    u.created_at.isoformat()    if u.created_at    else None,
                    "updated_at":    u.updated_at.isoformat()    if u.updated_at    else None,
                    "last_activity": u.last_activity.isoformat() if u.last_activity else None,
                }
                for u in users
            ]
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ── POST create user ──────────────────────────────────────────────────────────
@main_bp.route('/api/admin/users', methods=['POST'])
@admin_required
def api_create_user():
    """Create a new user."""
    body = request.get_json(force=True, silent=True) or {}

    username   = (body.get('username')   or '').strip()
    email      = (body.get('email')      or '').strip()
    password   = (body.get('password')   or '').strip()
    first_name = (body.get('first_name') or '').strip()
    last_name  = (body.get('last_name')  or '').strip()
    avatar     = (body.get('avatar')     or '👤').strip()
    is_admin   = bool(body.get('is_admin',  False))
    is_active  = bool(body.get('is_active', True))

    if not username: return jsonify({"success": False, "error": "username is required"}), 400
    if not email:    return jsonify({"success": False, "error": "email is required"}),    400
    if not password: return jsonify({"success": False, "error": "password is required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"success": False, "error": f"Username '{username}' already exists"}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "error": f"Email '{email}' already exists"}), 409

    try:
        user = User(
            username   = username,
            email      = email,
            first_name = first_name,
            last_name  = last_name,
            avatar     = avatar,
            is_admin   = is_admin,
            is_active  = is_active,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        send_welcome_email(user.email, user.username, password)
        return jsonify({"success": True, "message": "User created", "id": user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ── PUT update user ───────────────────────────────────────────────────────────
@main_bp.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def api_update_user(user_id):
    """Update an existing user."""
    user = User.query.get_or_404(user_id)
    body = request.get_json(force=True, silent=True) or {}

    email      = (body.get('email')      or '').strip()
    first_name = (body.get('first_name') or '').strip()
    last_name  = (body.get('last_name')  or '').strip()
    avatar     = (body.get('avatar')     or '👤').strip()
    password   = (body.get('password')   or '').strip()
    is_admin   = bool(body.get('is_admin',  user.is_admin))
    is_active  = bool(body.get('is_active', user.is_active))

    if not email:
        return jsonify({"success": False, "error": "email is required"}), 400

    # Check email uniqueness (excluding self)
    existing = User.query.filter_by(email=email).first()
    if existing and existing.id != user_id:
        return jsonify({"success": False, "error": f"Email '{email}' is already in use"}), 409

    try:
        user.email      = email
        user.first_name = first_name
        user.last_name  = last_name
        user.avatar     = avatar
        user.is_admin   = is_admin
        user.is_active  = is_active
        user.updated_at = datetime.utcnow()

        if password:                         # only update if provided
            user.set_password(password)

        db.session.commit()
        return jsonify({"success": True, "message": "User updated"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ── POST toggle active/inactive ───────────────────────────────────────────────
@main_bp.route('/api/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def api_toggle_user_status(user_id):
    """Activate or deactivate a user account."""
    # Prevent admin from deactivating their own account
    if user_id == current_user.id:
        return jsonify({"success": False, "error": "You cannot deactivate your own account"}), 400

    user = User.query.get_or_404(user_id)
    body = request.get_json(force=True, silent=True) or {}

    try:
        user.is_active  = bool(body.get('is_active', not user.is_active))
        user.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({
            "success":   True,
            "is_active": user.is_active,
            "message":   f"User {'activated' if user.is_active else 'deactivated'}"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ── DELETE user ───────────────────────────────────────────────────────────────
@main_bp.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def api_delete_user(user_id):
    """Permanently delete a user."""
    if user_id == current_user.id:
        return jsonify({"success": False, "error": "You cannot delete your own account"}), 400

    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"success": True, "message": f"User '{user.username}' deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
# ── Config ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # ← add one more .parent

AGENT_HISTORY_DIR = Path(os.getenv(
    "AGENT_HISTORY_DIR",
    str(BASE_DIR / "tmp" / "agent_history")
))
# ── Helper ───────────────────────────────────────────────────────────────────
def _scan_executions() -> list[dict]:
    """
    Scans AGENT_HISTORY_DIR and returns a list of execution metadata dicts,
    sorted newest-first (by folder mtime).
    """
    if not AGENT_HISTORY_DIR.exists():
        return []

    executions = []
    for folder in sorted(AGENT_HISTORY_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if not folder.is_dir():
            continue
        exec_id = folder.name
        json_path = folder / f"{exec_id}.json"
        gif_path  = folder / f"{exec_id}.gif"

        executions.append({
            "id":       exec_id,
            "has_json": json_path.exists(),
            "has_gif":  gif_path.exists(),
            "mtime":    folder.stat().st_mtime,
        })

    return executions


# ── Routes ───────────────────────────────────────────────────────────────────

@main_bp.route("/api/agent-history", methods=["GET"])
@login_required
def list_executions():
    """Return the list of all execution IDs with availability flags."""
    executions = _scan_executions()
    return jsonify({"executions": executions, "total": len(executions)})


@main_bp.route("/api/agent-history/<exec_id>/json", methods=["GET"])
@login_required
def get_execution_json(exec_id: str):
    """Return the JSON report for a given execution ID."""
    safe_id = Path(exec_id).name
    json_path = AGENT_HISTORY_DIR / safe_id / f"{safe_id}.json"

    if not json_path.exists():
        abort(404, description=f"No JSON found for execution {safe_id}")

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        abort(500, description=f"Invalid JSON: {e}")

    return jsonify(data)


@main_bp.route("/api/agent-history/<exec_id>/gif", methods=["GET"])
@login_required
def get_execution_gif(exec_id: str):
    """Stream the GIF recording for a given execution ID."""
    safe_id = Path(exec_id).name
    gif_path = AGENT_HISTORY_DIR / safe_id / f"{safe_id}.gif"

    if not gif_path.exists():
        abort(404, description=f"No GIF found for execution {safe_id}")

    return send_file(str(gif_path), mimetype="image/gif")


# ── DEBUG route (remove after fixing) ────────────────────────────────────────
@main_bp.route("/api/agent-history/debug", methods=["GET"])
def debug_history():
    """Debug route to check path and files — remove once working."""
    result = {
        "configured_path": str(AGENT_HISTORY_DIR),
        "base_dir": str(BASE_DIR),
        "exists": AGENT_HISTORY_DIR.exists(),
        "folders": []
    }

    if AGENT_HISTORY_DIR.exists():
        for folder in AGENT_HISTORY_DIR.iterdir():
            files = [f.name for f in folder.iterdir()] if folder.is_dir() else []
            result["folders"].append({
                "name": folder.name,
                "is_dir": folder.is_dir(),
                "files": files
            })

    return jsonify(result)









