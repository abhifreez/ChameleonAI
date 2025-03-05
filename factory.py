from models.gpt4_model import GPT4Model
from models.llama3_model import LLaMA3Model
from models.deepseek_model import DeepSeek
from models.gemini_model import GeminiModel

class ModelFactory:
    @staticmethod
    def get_model(model_name):
        if model_name == "gpt-4":
            return GPT4Model()
        elif model_name == "llama-3.1":
            return LLaMA3Model()
        elif model_name == "deepseek":
            return DeepSeek()
        elif model_name == "gemini-2.0-flash":
            return GeminiModel()
        else:
            return None
