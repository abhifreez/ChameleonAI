from abc import ABC, abstractmethod

class BaseLLM(ABC):
    """
    Abstract Base Class for LLMs.
    """

    @abstractmethod
    def format_prompt(self, system_prompt, user_prompt):
        pass

    @abstractmethod
    def format_prompt_messages(self, system_prompt, messages):
        pass

    @abstractmethod
    def generate_response(self, system_prompt, user_prompt):
        pass

    @abstractmethod
    def generate_response_messages(self, system_prompt, messages):
        pass


class BaseEmbedding(ABC):
    """
    Abstract Base Class for Embedding Models.
    """

    @abstractmethod
    def generate_embedding(self, text):
        pass