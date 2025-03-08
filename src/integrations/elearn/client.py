# src/integrations/elearn/client.py content
from typing import Dict, Any, List, Optional
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ELearnClient:
    """Client for interacting with SMU E-Learn API."""
    
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None, dummy_mode: bool = False):
        self.api_url = api_url or os.getenv('ELEARN_API_URL', 'https://elearn.smu.edu.sg/api')
        self.api_key = api_key or os.getenv('ELEARN_API_KEY', '')
        self.dummy_mode = dummy_mode
        
        if not self.api_key and not self.dummy_mode:
            raise ValueError("E-Learn API key is required. Set ELEARN_API_KEY environment variable.")
    
    def get_courses(self) -> List[Dict[str, Any]]:
        if self.dummy_mode:
            return [
                {
                    'code': 'IS621',
                    'title': 'Agile and DevSecOps',
                    'description': 'This course covers agile methodologies and DevSecOps practices for modern software development.',
                    'instructor': 'Dr. Smith',
                    'updated_at': '2023-01-15T10:30:00Z'
                },
                # Add more dummy courses as needed
            ]
        # Real implementation would go here
        return []

    def get_course(self, course_code: str) -> Optional[Dict[str, Any]]:
        if self.dummy_mode:
            return {
                'code': course_code,
                'title': 'Dummy Course',
                'description': 'This is a dummy course description.',
                'instructor': 'John Doe',
                'updated_at': '2023-01-15T10:30:00Z'
            }
        # Real implementation would go here
        return None

    def get_course_materials(self, course_code: str) -> List[Dict[str, Any]]:
        if self.dummy_mode:
            return [
                {'title': 'Lecture 1', 'url': 'http://example.com/lecture1'},
                {'title': 'Lecture 2', 'url': 'http://example.com/lecture2'}
            ]
        # Real implementation would go here
        return []

    def get_course_assignments(self, course_code: str) -> List[Dict[str, Any]]:
        if self.dummy_mode:
            return [
                {'title': 'Assignment 1', 'due_date': '2025-03-15'},
                {'title': 'Assignment 2', 'due_date': '2025-04-01'}
            ]
        # Real implementation would go here
        return []

    def get_course_schedule(self, course_code: str) -> List[Dict[str, Any]]:
        if self.dummy_mode:
            return [
                {'type': 'lecture', 'day': 'Monday', 'start_time': '10:00', 'end_time': '12:00', 'location': 'Room 301', 'instructor': 'Dr. Smith'},
                {'type': 'tutorial', 'day': 'Wednesday', 'start_time': '14:00', 'end_time': '16:00', 'location': 'Room 201', 'instructor': 'TA Johnson'}
            ]
        # Real implementation would go here
        return []

    def get_course_info(self, course_code):
        # Return dummy course information
        return {
            "course_code": course_code,
            "course_name": "Dummy Course",
            "instructor": "John Doe",
            "schedule": "Mondays and Wednesdays, 10:00 AM - 12:00 PM"
        }

    def get_assignments(self, course_code):
        # Return dummy assignments
        return [
            {"title": "Assignment 1", "due_date": "2025-03-15"},
            {"title": "Assignment 2", "due_date": "2025-04-01"}
        ]

    def get_learning_materials(self, course_code):
        # Return dummy learning materials
        return [
            {"title": "Lecture 1", "url": "http://example.com/lecture1"},
            {"title": "Lecture 2", "url": "http://example.com/lecture2"}
        ]