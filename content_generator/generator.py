from typing import List, Dict, Tuple, Callable
import os
from factory import ModelFactory
import json
from concurrent.futures import ThreadPoolExecutor
import threading

class ContentGenerator:
    def __init__(self, structure_model="deepseek", presentation_model="deepseek", notes_model="deepseek", max_parallel_topics=3, progress_callback: Callable[[str, float], None] = None):
        """
        Initialize with different models for each generation step
        Args:
            structure_model: Model to use for lecture structure generation
            presentation_model: Model to use for presentation generation
            notes_model: Model to use for detailed notes generation
            max_parallel_topics: Maximum number of topics to process in parallel
            progress_callback: Callback function to update progress
        """
        self.model_factory = ModelFactory()
        self.structure_model = self.model_factory.get_model(structure_model)
        self.presentation_model = self.model_factory.get_model(presentation_model)
        self.notes_model = self.model_factory.get_model(notes_model)
        self.prompt_dir = os.path.join(os.path.dirname(__file__), "prompts")
        self.max_parallel_topics = max_parallel_topics
        self._thread_local = threading.local()
        self.progress_callback = progress_callback
        
    def _load_prompt(self, prompt_file: str) -> str:
        """Load prompt from text file"""
        with open(os.path.join(self.prompt_dir, prompt_file), 'r') as f:
            return f.read()
            
    def _generate_lecture_detail(self, lecture_title: str, topics: List[str]) -> str:
        """Agent 1: Generates detailed lecture structure"""
        prompt = self._load_prompt("lecture_detail_prompt.txt")
        context = {
            "lecture_title": lecture_title,
            "topics": topics
        }
        # Convert context dict to string format for model input
        context_str = f"Lecture Title: {context['lecture_title']}\n\nTopics:\n"
        for topic in context['topics']:
            context_str += f"- {topic}\n"
        structured_content = self.structure_model.generate_response(prompt, context_str)
       
        return structured_content
        
    def _generate_presentation(self, lecture_detail: str) -> List[Dict]:
        """Agent 2: Generates PPT structure with slide content based on detailed lecture content"""
        prompt = self._load_prompt("presentation_prompt.txt")
        ppt_structure = self.presentation_model.generate_response(prompt, lecture_detail)
        return ppt_structure
        
    def _extract_important_topics(self, lecture_structure: str) -> List[Dict]:
        """
        Agent 3.1: Extract important topics from lecture structure
        Returns list of topics with their context
        """
        prompt = self._load_prompt("topic_extraction_prompt.txt")
        topics_json = self.notes_model.generate_response(prompt, lecture_structure)
      

        # try:
        #     # Handle different response formats
        #     if isinstance(topics_json, list):
        #         topics = topics_json
        #     elif isinstance(topics_json, str):
        #         # Clean the string of any markdown formatting
        #         cleaned_json = topics_json.replace('```json', '').replace('```', '').strip()
        #         topics = json.loads(cleaned_json)
        #     else:
        #         raise ValueError(f"Unexpected response type: {type(topics_json)}")
           
        #     # Validate the structure of each topic
          
        #     return topics
        # except json.JSONDecodeError as e:
        #     raise ValueError(f"Failed to parse topics from model output: {str(e)}")
        try:
            if isinstance(topics_json, list):
                return topics_json
            elif isinstance(topics_json, str):
                cleaned = topics_json.replace('```json', '').replace('```', '').strip()
                topics = json.loads(cleaned)
                if isinstance(topics, dict) and "topics" in topics:
                    return topics["topics"]
                elif isinstance(topics, list):
                    return topics
                else:
                    raise ValueError("Unexpected JSON structure")
            else:
                raise ValueError(f"Unexpected response type: {type(topics_json)}")
        except Exception as e:
            raise ValueError(f"Failed to parse important topics: {e}")
    
    def _generate_topic_notes(self, topic: str, topic_json: str) -> str:
        """
        Agent 3.2: Generates detailed notes for a specific topic
        """
        prompt = self._load_prompt("topic_notes_prompt.txt")

        topic_note = self.notes_model.generate_response(prompt, topic_json)
        formatted_note = f"\n\nTopic: {topic}\n\n{topic_note}\n\n"
       

        note = {
            "topic": topic,
            "topic_json": topic_note
        }
        
        return note
        
    def _get_thread_model(self):
        """Get or create a thread-local model instance"""
        if not hasattr(self._thread_local, 'model'):
            self._thread_local.model = self.model_factory.get_model(self.notes_model)
        return self._thread_local.model
        
    def _generate_notes(self, lecture_structure: str) -> str:
        """
        Agent 3: Generates detailed notes using a two-step process
        1. Extract important topics
        2. Generate detailed notes for each topic
        """
        extracted_topics = self._extract_important_topics(lecture_structure)

        all_notes = []
        # if "topics" not in extracted_topics:
        #     raise ValueError("Extracted topics do not contain 'topics' key")
        # topics = extracted_topics["topics"]

        # all_notes = []
        # for topic in topics:
        #     topic_json = json.dumps(topic)
        #     # Generate notes for the main topic
        #     all_notes.append(self._generate_topic_notes(topic, topic_json))
        for topic in extracted_topics:
            topic_name = topic.get("name", "Untitled Topic")
            topic_json = json.dumps(topic, indent=2)
            try:
                topic_note = self._generate_topic_notes(topic_name, topic_json)
                all_notes.append(topic_note)
            except Exception as e:
                print(f"Error generating notes for topic '{topic_name}': {e}")
                continue

        return self._format_combined_notes(all_notes, "Lecture Notes")
    
    def _format_combined_notes(self, topic_notes: List[Dict], title: str) -> str:
        """Format all topic notes into a cohesive document"""
        header = ""
        toc = "\n".join([f"- {note['topic']}" for note in topic_notes])
        formatted_notes = "\n\n".join([f"## {note['topic']}\n\n{note['topic_json']}" for note in topic_notes])
        return header + toc + "\n\n" + formatted_notes
    
    
   
        
    def _update_progress(self, stage: str, progress: float):
        """Update generation progress"""
        if self.progress_callback:
            self.progress_callback(stage, progress)

    def _json_to_dict(self, json_str: str) -> Dict:
        """Convert JSON string to dictionary"""
        try:
            # Clean the JSON markup or any other thing as output is
            cleaned_json_str = json_str.replace('```json', '').replace('```', '').strip()
            return json.loads(cleaned_json_str)
        except json.JSONDecodeError as e:
            self._update_progress("JSON decoding error", 0.0)
            raise ValueError(f"Invalid JSON: {e}")
            
    def generate_content(self, lecture_title: str, topics: List[str]) -> Tuple[List[Dict], str]:
        print("Inside generate_content function ------>")
        self._update_progress("Starting content generation", 0.0)
        
        # Step 1: Generate lecture structure
        self._update_progress("Generating lecture structure", 0.1)
        lecture_details = self._generate_lecture_detail(lecture_title, topics)
        lecture_details_file = self._write_text_to_file(lecture_details)
        
        
        # Step 2: Generate PPT structure
        self._update_progress("Generating presentation structure", 0.3)
        ppt_structure = self._generate_presentation(lecture_details)
        ppt_structure = self._json_to_dict(ppt_structure)
        

        # Step 3: Generate detailed notes
        self._update_progress("Extracting topics", 0.5)
        notes = self._generate_notes(lecture_details)
        print(f"Final Notes:\n{notes}")
        notes_file = self._write_text_to_file(notes)

        
        self._update_progress("Completed", 1.0)
        return ppt_structure,lecture_details_file, notes_file

    @classmethod
    def available_models(cls) -> List[str]:
        """Returns list of available models that can be used"""
        return ModelFactory.get_available_models() 
    
    def _write_text_to_file(self, text: str) -> str:
        """Write text to a file with a timestamped filename and return the file URL"""
        import os
        from datetime import datetime

        # Create directory if it doesn't exist
        directory = "generated_content"
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{directory}/{timestamp}_details.txt"

        # Write text to file
        with open(filename, 'w') as file:
            file.write(text)

        # Return the file URL
        return os.path.abspath(filename)