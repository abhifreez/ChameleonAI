from flask import Flask, request, jsonify
from factory import ModelFactory
from dotenv import load_dotenv
import os
import json
import re

# Load environment variables from .env file
load_dotenv()



app = Flask(__name__)

API_KEY = os.getenv("API_KEY")

ds_local_model = ModelFactory().get_model("deepseek")

def verify_api_key(api_key):
    """Check if the provided API key is valid."""
    return api_key == API_KEY

def load_system_prompt(filename="system_prompt.txt"):
    """Load system prompt from a text file."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "You are an AI assistant."
    
def convert_to_ace_format(review_json):
    """
    Converts the given review JSON into ACE JSON format.
    """
    ace_format = {
        "comments": []
    }
    
    for review in review_json.get("reviews", []):
        ace_format["comments"].append({
            "pattern": f"^.*$",  # Matches the entire line containing the issue
            "comment": review["reviewComment"]
        })
    
    return ace_format

def json_to_dict(json_string):
    """
    Converts a JSON string into a Python dictionary.
    Handles escape sequences properly.
    """
    try:
        json_string = re.sub(r"^```[a-zA-Z]*\n|\n```$", "", json_string.strip())
        return json.loads(json_string)
    except json.JSONDecodeError:
        return json.loads(json_string.encode().decode('unicode_escape'))


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

@app.route("/embedding", methods=["POST"])
def generate_embedding():
    api_key = request.headers.get("X-API-Key")
    if not api_key or not verify_api_key(api_key):
        return jsonify({"error": "Invalid or missing API key"}), 403
    data = request.json
    model_name = data.get("model_name")
    user_prompt = data.get("user_prompt")

    if not model_name or not user_prompt:
        return jsonify({"error": "Missing model_name or user_prompt"}), 400

    model = ModelFactory.get_model(model_name)
    if not model:
        return jsonify({"error": "Invalid model name"}), 400

    response_text = model.generate_embedding(user_prompt)
    
    return jsonify({
        "model": model_name,
        "response": response_text
    })


@app.route("/reviewpr", methods=["POST"])
def review_pr():
    #a = json_to_dict("```json\n{\n  \"reviews\": [\n    {\n      \"lineNumber\": 99,\n      \"reviewComment\": \"The code incorrectly accesses `paid_status` instead of `payment_status_total_due` in the condition. This may lead to incorrect totals for overduing and outstanding amounts.\"\n    },\n    {\n      \"lineNumber\": 100,\n      \"reviewComment\": \"The code incorrectly accesses `paid_status` instead of `payment_status_total_due` in the condition. This may lead to incorrect totals for overduing and outstanding amounts.\"\n    }\n  ]\n}\n```")
    
 
    api_key = request.headers.get("X-API-Key")
    if not api_key or not verify_api_key(api_key):
        return jsonify({"error": "Invalid or missing API key"}), 403
    data = request.json
    model_name = "deepseek"
   
    
    system_prompt = load_system_prompt("system_prompts/review_prompt.txt")
    user_prompt =  data.get("user_prompt")

    if not model_name or not user_prompt:
        return jsonify({"error": "Missing model_name or user_prompt"}), 400
    
    if(model_name == "deepseek"):
        model = ds_local_model
    else:
        model = ModelFactory.get_model(model_name)
    if not model:
        return jsonify({"error": "Invalid model name"}), 400
  
    response_text = json_to_dict(model.generate_response(system_prompt, user_prompt))
    #response_text_2 = gpt_model.generate_response("Generate a valid JSON file that an Ava test script can parse.", response_text)
    
    return jsonify({
        "model": model_name,
        "response": response_text
    })


if __name__ == "__main__":
    app.run(debug=True)
