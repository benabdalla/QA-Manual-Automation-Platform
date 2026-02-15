import os
import google.generativeai as genai

# Authentification à l'API Gemini via clé d'API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialisation du modèle Gemini Flash
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

# Message système et prompt utilisateur
prompt = [
  "Define 1 Test Case for the provided requirement specification. Response must be simple list with Description and test steps. No additional instructions.",
  "Data Precision and Accuracy. Requirement description: Connectivity Unit shall not miss more than 1 message per 100000 transferred ones. Missed messages shall be logged into errors list."
]

# Envoi de la requête à Gemini Flash
response = model.generate_content(prompt)

# Affichage de la réponse
print(response.text)
