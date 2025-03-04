from flask import Flask, request, jsonify
from factory import ModelFactory

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate_text():
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
