#meta-llama/Meta-Llama-3-8B
from transformers import AutoModelForCausalLM, AutoTokenizer

# Define the model name
model_name = "meta-llama/Meta-Llama-3.1-8B"

# Set local directory
local_model_path = f"/Users/abhinavagarwal/Documents/Models/transformers{model_name}"

print("Downloading LLaMA model...")

# Download and save
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

tokenizer.save_pretrained(local_model_path)
model.save_pretrained(local_model_path)

print(f"✅ Model saved at {local_model_path}")

