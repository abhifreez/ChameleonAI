from google import genai
import os
from models.base_model import BaseLLM
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()
model = "gemini-2.0-flash"
# Set API Key



class GeminiModel(BaseLLM):
    def __init__(self):
       self.model = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            
    def format_prompt(self, system_prompt, user_prompt):
        return f"{system_prompt}\nUser: {user_prompt}\n AI:"

    def generate_response(self, system_prompt, user_prompt):
        formatted_prompt = self.format_prompt(system_prompt, user_prompt)
        response = self.model.models.generate_content(model="gemini-2.0-flash",
                                                    contents=formatted_prompt)
        return response.text if response and hasattr(response, "text") else ""
