# src/nlp/entity_extractor.py content
import re
from typing import Dict, List

class EntityExtractor:
    """Extract entities from user messages."""

    def __init__(self):
        # Define entity patterns
        self.entity_patterns = {
            'course_code': r'IS\s*(\d{3})',
            'date': r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            'time': r'(\d{1,2}:\d{2}(?:\s*[aApP][mM])?)',
            'email': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            'percentage': r'(\d{1,3}(?:\.\d+)?)\s*%',
            'number': r'\b(\d+)\b'
        }
        
        # Define course names mapping
        self.course_names = {
            'IS621': 'Agile and DevSecOps',
            'IS622': 'Cloud Computing and Container Architecture',
            'IS623': 'AI and Machine Learning',
            'IS624': 'Big Data and Analytics',
            'IS625': 'Software Quality Management'
        }

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities from the given text.
        
        Args:
            text: The input text to extract entities from
            
        Returns:
            A dictionary mapping entity types to lists of extracted values
        """
        result = {}
        
        # Extract entities using regex patterns
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                result[entity_type] = matches
        
        # Special handling for course codes
        if 'course_code' in result:
            course_names = []
            for code in result['course_code']:
                full_code = f'IS{code}'
                if full_code in self.course_names:
                    course_names.append(self.course_names[full_code])
            
            if course_names:
                result['course_name'] = course_names
        
        return result