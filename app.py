from flask import Flask, request, jsonify
from flask_cors import CORS

import requests

app = Flask(__name__)
CORS(app) 

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
API = "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"

def query_huggingface_api(prompt):
    """Send the prompt to the Hugging Face model and return the response."""
    headers = {"Authorization": f"Bearer {API}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.5,
            "top_p": 0.8,
            "frequency_penalty": 0.5,

            "presence_penalty": 0.5
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        print("Hugging Face API Response:", response.json())  # Debugging step
        return response.json()
    else:
        raise Exception(f"Hugging Face API error: {response.status_code} - {response.text}")

@app.route('/query', methods=['POST'])
def process_query():
    """Process incoming query requests."""
    if not request.is_json:
        return jsonify({'message': 'Content-Type must be application/json'}), 400

    data = request.get_json(silent=True)
    if not data or 'prompt' not in data:
        return jsonify({'message': 'Missing or invalid prompt'}), 400

    prompt = data['prompt']

    try:
        hf_response = query_huggingface_api(prompt)

        if isinstance(hf_response, list) and len(hf_response) > 0:
            generated_text = hf_response[0].get("generated_text", "").strip()
        else:
            generated_text = hf_response.get("generated_text", "").strip()

        if not generated_text:
            return jsonify({'answer': 'No response generated by the model'}), 200

        return jsonify({'answer': generated_text}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5088)
