from typing import List, Dict, Tuple, Callable
import os
from factory import ModelFactory
import json
from concurrent.futures import ThreadPoolExecutor
import threading


class HardwareGenerator:
    def __init__(self, model="deepseek", progress_callback: Callable[[str, float], None] = None):
        """
        Initialize with a model for hardware manufacturing query processing
        Args:
            model: Model to use for answering hardware manufacturing queries
            progress_callback: Callback function to update progress
        """
        self.model_factory = ModelFactory()
        self.model = self.model_factory.get_model(model)
        self.prompt_dir = os.path.join(os.path.dirname(__file__), "prompts")
        self.progress_callback = progress_callback
        
    def _load_prompt(self, prompt_file: str) -> str:
        """Load prompt from text file"""
        with open(os.path.join(self.prompt_dir, prompt_file), 'r') as f:
            return f.read()
    
    def _update_progress(self, stage: str, progress: float):
        """Update generation progress"""
        if self.progress_callback:
            self.progress_callback(stage, progress)

    def answer_hardware_query(self, query: str) -> str:
        """
        Process a user query related to hardware manufacturing and provide a response
        based on the system prompt and knowledge base
        
        Args:
            query: The user's question about hardware manufacturing
            
        Returns:
            A detailed response to the user's hardware manufacturing query
        """
        self._update_progress("Processing hardware query", 0.1)
        
        # Load the system prompt that defines how to respond to hardware manufacturing queries
        system_prompt = self._load_prompt("generic.txt")
        
        # Generate response based on the system prompt and user query
        self._update_progress("Generating response", 0.5)
        response = self.model.generate_response(system_prompt, query)
        

        
        self._update_progress("Completed", 1.0)
        return response

    @classmethod
    def available_models(cls) -> List[str]:
        """Returns list of available models that can be used"""
        return ModelFactory.get_available_models() 
    
    def _write_text_to_file(self, text: str, name: str) -> str:
        """Write text to a file with a timestamped filename and return the file URL"""
        import os
        from datetime import datetime

        # Create directory if it doesn't exist
        directory = "generated_content"
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{directory}/{timestamp}_{name}.txt"

        # Write text to file
        with open(filename, 'w') as file:
            file.write(text)

        # Return the file URL
        return os.path.abspath(filename)