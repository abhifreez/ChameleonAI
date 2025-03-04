from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from models.base_model import BaseLLM

class LLaMA3Model(BaseLLM):
    def __init__(self):
        local_model_path = "./local_models/llama-2-7b"

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B")

        # Load model with 4-bit quantization
        self.model = AutoModelForCausalLM.from_pretrained(
            "meta-llama/Llama-3.1-8B",
            device_map="auto",  
            load_in_4bit=True,  # Enable 4-bit quantization
            torch_dtype=torch.float16,
        )

        # Initialize pipeline
        self.pipeline = pipeline(
            "text-generation", model=self.model, tokenizer=self.tokenizer
        )

    def format_prompt(self, system_prompt, user_prompt):
        return f"<<SYS>> {system_prompt} <</SYS>>\n[USER]: {user_prompt}\n[AI]:"

    def generate_response(self, system_prompt, user_prompt):
        formatted_prompt = self.format_prompt(system_prompt, user_prompt)
        response = self.pipeline(formatted_prompt, max_length=200)
        return response[0]["generated_text"]
