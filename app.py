from flask import Flask, request, jsonify
from factory import ModelFactory
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")

def verify_api_key(api_key):
    """Check if the provided API key is valid."""
    return api_key == API_KEY

@app.route("/generate", methods=["POST"])
def generate_text():
    api_key = request.headers.get("X-API-Key")
    if not api_key or not verify_api_key(api_key):
        return jsonify({"error": "Invalid or missing API key"}), 403
    data = request.json
    model_name = data.get("model_name")
    system_prompt = data.get("system_prompt", "You are an AI assistant.")
    user_prompt = data.get("user_prompt")

    if not model_name or not user_prompt:
        return jsonify({"error": "Missing model_name or user_prompt"}), 400

    model = ModelFactory.get_model(model_name)
    if not model:
        return jsonify({"error": "Invalid model name"}), 400

    response_text = model.generate_response(system_prompt, user_prompt)
    
    return jsonify({
        "model": model_name,
        "response": response_text
    })



if __name__ == "__main__":
    app.run(debug=True)
