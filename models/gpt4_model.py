import openai
import os
from models.base_model import BaseLLM
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set API Key
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)




class GPT4Model(BaseLLM):
    def format_prompt(self, system_prompt, user_prompt):
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    def generate_response(self, system_prompt, user_prompt):
        formatted_prompt = self.format_prompt(system_prompt, user_prompt)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=formatted_prompt
        )
        return response.choices[0].message.content  # ✅ Use dot notation

