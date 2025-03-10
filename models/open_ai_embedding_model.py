import os
import openai
from models.base_model import BaseEmbedding
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("AZURE_OPENAI_API_KEY")
base_url = os.getenv("AZURE_OPENAI_ENDPOINT")
client = AzureOpenAI(
  api_key = api_key,  
  api_version = "2023-05-15",
  azure_endpoint = base_url
)

class AzureOpenAIEmbeddingLLM(BaseEmbedding):
    """
    Subclass for handling embedding generation using Azure OpenAI.
    """

    def generate_embedding(self, text):
        # API call to generate embeddings using Azure's OpenAI API
        try:
            response = client.embeddings.create(
                model="text-embedding-ada-002",  # Azure's embedding model
                input=text
            )
            # Return the embedding from the response
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
