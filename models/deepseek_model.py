from llama_cpp import Llama
import torch
from models.base_model import BaseLLM
import os
import re

def extract_response(message):
    content = message.get("content", "")
    # Remove everything between <think> and </think> including the tags
    output = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
    return output

# Example Usage
message = {"content": "<think>ss</think>shgashdhsh"}
clean_output = extract_response(message)
print(clean_output)  # Output: "shgashdhsh"

class DeepSeek(BaseLLM):
    def __init__(self):
        

        MODEL_PATH = "/Users/abhinavagarwal/Documents/Models/lmstudio-community/DeepSeek-R1-Distill-Qwen-7B-GGUF/DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf"

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

        self.model= Llama(
            model_path=MODEL_PATH,
            n_gpu_layers=100,  # Utilize GPU for better performance (Mac Metal supported)
            n_ctx=2048,  # Context window size
            n_threads=6  # Optimize for Apple M1/M2/M3 CPU threads
        )

    def format_prompt(self, system_prompt, user_prompt):
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    def generate_response(self, system_prompt, user_prompt):
        formatted_prompt = self.format_prompt(system_prompt, user_prompt)
        response = self.model.create_chat_completion(formatted_prompt,stream=False)
        #clean_output = extract_response(response.response.choices[0].message.content)
        a = response["choices"][0]["message"]
        clean_output = extract_response(a)
        return clean_output
        # return response["choices"][0] # ✅ Use dot notation
