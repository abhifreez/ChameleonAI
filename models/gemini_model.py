from google import genai
import os
from models.base_model import BaseLLM
from dotenv import load_dotenv
import json
from google.genai import types


# Load environment variables from .env file
load_dotenv()
model = "gemini-2.0-flash"
# Set API Key



class GeminiModel(BaseLLM):

    
    def __init__(self):
       self.model = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def format_prompt_messages(self, system_prompt, messages):

        # Print message type for debugging
        print(f"Received messages type: {type(messages)}")
        if messages:
            if isinstance(messages, list) and len(messages) > 0:
                print(f"First message type: {type(messages[0])}")
                if isinstance(messages[0], dict):
                    print(f"First message keys: {messages[0].keys()}")
        # Process the messages list
        if not isinstance(messages, list):
            # Convert to list if it's not already
            messages = [messages]
            
        # Check if messages is already in the expected format with role/content
        if messages and isinstance(messages[0], dict) and "role" in messages[0]:
            return [
                {"role": "user", "content": system_prompt},
                *messages
            ]
        
        # If messages is a JSON string, try to parse it
        if len(messages) == 1 and isinstance(messages[0], str):
            try:
                parsed_messages = json.loads(messages[0])
                if isinstance(parsed_messages, list):
                    if parsed_messages and isinstance(parsed_messages[0], dict) and "role" in parsed_messages[0]:
                        return [
                            {"role": "system", "content": system_prompt},
                            *parsed_messages
                        ]
                    else:
                        formatted_messages = [{"role": "user", "content": msg} for msg in parsed_messages]
                        return [
                            {"role": "system", "content": system_prompt},
                            *formatted_messages
                        ]
            except json.JSONDecodeError:
                pass
        
        # Default handling: convert each message to proper format
        formatted_messages = [{"role": "user", "content": message} for message in messages]
        return [
            {"role": "system", "content": system_prompt},
            *formatted_messages
        ]

            
    def format_prompt(self, system_prompt, user_prompt):
        return f"{system_prompt}\nUser: {user_prompt}\n AI:"

    def generate_response(self, system_prompt, user_prompt):
        formatted_prompt = self.format_prompt(system_prompt, user_prompt)
        response = self.model.models.generate_content(model="gemini-2.0-flash",
                                                    contents=formatted_prompt)
        return response.text if response and hasattr(response, "text") else ""
    
    def generate_response_messages(self, system_prompt, messages):
        print("messages", messages)
        formatted_messages = self.format_prompt_messages(system_prompt, messages)
        
        # Convert to Google's Content and Part types
        history = []
        for msg in formatted_messages:
            role = "model" if msg["role"] == "assistant" else msg["role"]
            history.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=msg["content"])]
                )
            )
        
        print("chat history", history)
        # Create chat with history
        chat = self.model.chats.create(
            model="gemini-2.0-flash",
            history=history[:-1]  # All messages except the last one
        )
      
        
        # Send the last message
        last_message = formatted_messages[-1]["content"]
        response = chat.send_message(message=last_message)
        
        return response.text if response and hasattr(response, "text") else ""
