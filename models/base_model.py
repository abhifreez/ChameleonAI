from abc import ABC, abstractmethod

class BaseLLM(ABC):
    """
    Abstract Base Class for LLMs.
    """

    @abstractmethod
    def format_prompt(self, system_prompt, user_prompt):
        pass

    @abstractmethod
    def generate_response(self, system_prompt, user_prompt):
        pass
