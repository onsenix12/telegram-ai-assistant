# src/nlp/intent_classifier.py content
import re
from typing import Dict, List, Tuple

class IntentClassifier:
    """Basic intent classifier for the AI Learning Assistant."""
    
    def __init__(self):
        # Define intents and their patterns
        self.intent_patterns = {
            'greeting': [
                r'hello', r'hi', r'hey', r'greetings', r'good morning', 
                r'good afternoon', r'good evening'
            ],
            'farewell': [
                r'bye', r'goodbye', r'see you', r'talk to you later', 
                r'have a good day'
            ],
            'help': [
                r'help', r'assist', r'support', r'guidance', r'how do I'
            ],
            'course_info': [
                r'course', r'class', r'module', r'subject', r'IS\d{3}', 
                r'information about', r'tell me about', r'details on'
            ],
            'assignment': [
                r'assignment', r'homework', r'project', r'task', r'submission',
                r'deadline', r'due date', r'when is', r'submit'
            ],
            'grades': [
                r'grade', r'score', r'mark', r'performance', r'result',
                r'how did I do', r'passed', r'failed'
            ],
            'schedule': [
                r'schedule', r'timetable', r'calendar', r'when', r'what time',
                r'date', r'class time', r'lecture', r'session'
            ],
            'learning_material': [
                r'material', r'document', r'reading', r'textbook', r'note',
                r'slide', r'resource', r'learn', r'study'
            ]
        }
        
    def classify(self, text: str) -> Tuple[str, float]:
        """
        Classify the intent of the given text.
        
        Args:
            text: The input text to classify
            
        Returns:
            A tuple containing the intent name and confidence score
        """
        text = text.lower()
        scores = {}
        
        # Calculate score for each intent
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                score += len(matches)
            
            if score > 0:
                # Normalize score based on number of patterns
                scores[intent] = score / len(patterns)
        
        # Get the highest scoring intent
        if scores:
            top_intent = max(scores.items(), key=lambda x: x[1])
            return top_intent
        else:
            return ('unknown', 0.0)
    
    def get_all_scores(self, text: str) -> Dict[str, float]:
        """
        Get scores for all intents for the given text.
        
        Args:
            text: The input text to classify
            
        Returns:
            A dictionary mapping intent names to confidence scores
        """
        text = text.lower()
        scores = {}
        
        # Calculate score for each intent
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                score += len(matches)
            
            if score > 0:
                # Normalize score based on number of patterns
                scores[intent] = score / len(patterns)
            else:
                scores[intent] = 0.0
        
        return scores