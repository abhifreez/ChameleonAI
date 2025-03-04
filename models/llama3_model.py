from transformers import pipeline
from models.base_model import BaseLLM

class LLaMA3Model(BaseLLM):
   def __init__(self):
        # Load the model from the local directory
        local_model_path = "./local_models/llama-2-7b"

        self.pipeline = pipeline(
            "text-generation",
            model=local_model_path,
            device=0  # Use GPU if available, else CPU
        )

   def format_prompt(self, system_prompt, user_prompt):
        return f"<<SYS>> {system_prompt} <</SYS>>\n[USER]: {user_prompt}\n[AI]:"

   def generate_response(self, system_prompt, user_prompt):
        formatted_prompt = self.format_prompt(system_prompt, user_prompt)
        response = self.pipeline(formatted_prompt, max_length=200)
        return response[0]["generated_text"]
