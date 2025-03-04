from models.gpt4_model import GPT4Model
from models.llama3_model import LLaMA3Model


class ModelFactory:
    @staticmethod
    def get_model(model_name):
        if model_name == "gpt-4":
            return GPT4Model()
        elif model_name == "llama-3.1":
            return LLaMA3Model()
        else:
            return None
