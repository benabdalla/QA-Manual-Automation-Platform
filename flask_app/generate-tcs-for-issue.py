import os
import re

import requests
from requests.auth import HTTPBasicAuth
import json
import openai
import google.generativeai as genai
from flask import Flask, render_template, request, redirect, url_for, app, jsonify

import argparse
# from test_case_parser import filter_test_cases

# from generate_json import generate_with_openai

OPENAI_TOKEN_FILE = 'openai_token.txt'  # https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key
AI_MODEL = "gemini-2.0-flash"  # "gpt-3.5-turbo"

# Jira Cloud configuration
JIRA_TOKEN_FILE = 'jira_token.txt'  # https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/

# Jira Cloud API endpoint for creating issues (test cases)
XRAY_URL = "https://xray.cloud.getxray.app/api/v2/import/test/bulk"
XRAY_AUTH_JSON = 'xray_auth.json'  # File containing your XRAY API token https://community.atlassian.com/t5/Jira-Software-questions/Where-to-create-Xray-api-key/qaq-p/1923024

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


def generate_with_openai(prompt, project_key, version_name, folder_path, tc_amount, skip_checks=False, debug=True, app=None):
    """Generate test cases using Google Generative AI
    
    Args:
        app: Flask app instance for file path resolution (optional)
    """
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
    json_result = clean_api_response(json_result)
    if json_result is None:
        print("❌ Failed to parse JSON from response")
        return None
    
    # Parse JSON string to object for validation
    try:
        json_data = json.loads(json_result)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {e}")
        return None
    
    if debug:
        print("Parsed JSON:", json_result)
        print("✅ Generation Done.")
    
    # Filter test cases if needed
    # if not skip_checks:
    #     filtered_json_output = filter_test_cases(json_data)
    # else:
    filtered_json_output = json_data
    
    # Save to file with proper path resolution
    if app:
        json_file_path = os.path.join(app.root_path, 'static', 'data', 'output_tc.json')
    else:
        json_file_path = os.path.join(os.path.dirname(__file__), 'static', 'data', 'output_tc.json')
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
    
    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(filtered_json_output, file, indent=2, ensure_ascii=False)
    
    return filtered_json_output

def import_test_cases_to_xray(app=None):
    """Import generated test cases to Xray
    
    Args:
        app: Flask app instance for file path resolution (optional)
    """
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
    
    # Resolve file path with proper app context
    if app:
        json_file_path = os.path.join(app.root_path, 'static', 'data', 'output_tc.json')
    else:
        json_file_path = os.path.join(os.path.dirname(__file__), 'static', 'data', 'output_tc.json')
    
    # Open the file for reading
    with open(json_file_path, 'r', encoding='utf-8') as f:
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


def main(req, username, baseurl, project_key, version_name, folder_path, tc_amount, skip_checks, del_tc, debug, app=None):
    """Generate test cases from Jira requirement
    
    Args:
        app: Flask app instance for file path resolution (optional)
    """
    url = baseurl + '/rest/api/2'
    resultatJson = ""
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
    #     generate_with_openai(req_data,project_key,version_name,folder_path, tc_amount, skip_checks, app=app)
    #     # import_test_cases_to_xray(req, debug)
    # else:
    #     # if input("Generate Test Cases: [y]/n?") != "n":
    resultatJson = generate_with_openai(req_data, project_key, version_name, folder_path, tc_amount, skip_checks, app=app)
        # import_test_cases_to_xray(req, debug)
    return resultatJson




app = Flask(__name__)

@app.route('/resultat')
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


@app.route('/save_tests', methods=['POST'])
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



@app.route('/import-xray', methods=['POST'])
def import_xray():
    try:
        # Simule une importation
        import_test_cases_to_xray()
        print("import_test_cases_to_xray called")
        return render_template("index.html", result="data insert.")
    except Exception as e:
        print(f"Erreur Xray: {e}")
        return redirect(url_for('resultat'))



if __name__ == '__main__':
    # Host '0.0.0.0' allows access from other devices on the same network
    app.run(host='0.0.0.0', port=5001, debug=True)