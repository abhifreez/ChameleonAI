from llama_cpp import Llama
import torch
from models.base_model import BaseLLM
import os
import re
from dotenv import load_dotenv
from transformers import pipeline
import json

load_dotenv()

model_path = os.getenv("LOCAL_MODEL_GEMMA3")
def extract_response(message):
    content = message.get("content", "")
    # Remove everything between <think> and </think> including the tags
    output = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
    return output

# Example Usage
message = {"content": "<think>ss</think>shgashdhsh"}
clean_output = extract_response(message)
print(clean_output)  # Output: "shgashdhsh"

class Gemma3(BaseLLM):
    def __init__(self):
        

  

     # Load model directly


        pipe = pipeline("image-text-to-text", model="google/gemma-3-4b-it")



        #MODEL_PATH = "/Users/abhinavagarwal/Documents/Models/lmstudio-community/DeepSeek-R1-Distill-Qwen-7B-GGUF/DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf"
        # MODEL_PATH = model_path

        # if not os.path.exists(MODEL_PATH):
        #     raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

        # self.model= Llama(
        #     model_path=MODEL_PATH,
        #     n_gpu_layers=80,  # Utilize GPU for better performance (Mac Metal supported)
        #     n_ctx=2048*3,  # Context window size
        #     n_threads=8,  # Optimize for Apple M1/M2/M3 CPU threads
        #     n_batch = 1024,
        #     use_mlock = True
        # )

    def format_prompt(self, system_prompt, user_prompt):
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    def format_prompt_messages(self, system_prompt, messages):
        # Check if messages is already in the expected format
        if messages and isinstance(messages, list) and isinstance(messages[0], dict) and "role" in messages[0]:
            # Messages are already in the correct format, return as is
            print(f"Message type: {type(messages)}")
            return [
                {"role": "system", "content": system_prompt},
                *messages
            ]
        
        # If messages is a JSON string, try to parse it
        if isinstance(messages, str):
            try:
                parsed_messages = json.loads(messages)
                print(f"Message type: {type(messages)} (JSON string)")
                if isinstance(parsed_messages, list):
                    if parsed_messages and isinstance(parsed_messages[0], dict) and "role" in parsed_messages[0]:
                        return [
                            {"role": "system", "content": system_prompt},
                            *parsed_messages
                        ]
                    else:
                        messages = [{"role": "user", "content": msg} for msg in parsed_messages]
                        return [
                            {"role": "system", "content": system_prompt},
                            *messages
                        ]
            except json.JSONDecodeError:
                # Not a valid JSON string, continue with default handling
                print(f"Message type: {type(messages)} (not valid JSON)")
                pass
        
        print(f"Message type: {type(messages)} (default handling)")
        messages = [{"role": "user", "content": message} for message in messages]
        return [
            {"role": "system", "content": system_prompt},
            *messages
        ]

    def generate_response(self, system_prompt, user_prompt):
        formatted_prompt = self.format_prompt(system_prompt, user_prompt)
        response = self.model.create_chat_completion(formatted_prompt,stream=False)
        #clean_output = extract_response(response.response.choices[0].message.content)
        a = response["choices"][0]["message"]
        clean_output = extract_response(a)
        return clean_output
        # return response["choices"][0] # ✅ Use dot notation

    def generate_response_messages(self, system_prompt, messages):
        formatted_prompt = self.format_prompt_messages(system_prompt, messages)
        response = self.model.create_chat_completion(formatted_prompt,stream=False)
        a = response["choices"][0]["message"]
        clean_output = extract_response(a)
        return clean_output