# src/admin/faq/faq_manager.py content
from typing import Dict, Any, List, Optional
import json
import os
import time
from datetime import datetime

class FAQManager:
    """Manage frequently asked questions."""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.faq_file = os.path.join(data_dir, 'faqs.json')
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize FAQ file if not exists
        if not os.path.exists(self.faq_file):
            with open(self.faq_file, 'w') as f:
                json.dump({
                    'faqs': [],
                    'categories': []
                }, f)
    
    def add_faq(self, question: str, answer: str, category: str = 'General') -> Dict[str, Any]:
        """
        Add a new FAQ.
        
        Args:
            question: The question text
            answer: The answer text
            category: The category for the question
            
        Returns:
            The newly added FAQ dictionary
        """
        # Load FAQs
        data = self._load_data()
        
        # Create new FAQ
        faq_id = str(int(time.time()))
        faq = {
            'id': faq_id,
            'question': question,
            'answer': answer,
            'category': category,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Add to list
        data['faqs'].append(faq)
        
        # Add category if not exists
        if category not in data['categories']:
            data['categories'].append(category)
        
        # Save data
        self._save_data(data)
        
        return faq
    
    def update_faq(self, faq_id: str, question: Optional[str] = None,
                   answer: Optional[str] = None, category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Update an existing FAQ.
        
        Args:
            faq_id: The ID of the FAQ to update
            question: Optional new question text
            answer: Optional new answer text
            category: Optional new category
            
        Returns:
            The updated FAQ dictionary or None if not found
        """
        # Load FAQs
        data = self._load_data()
        
        # Find FAQ by ID
        for i, faq in enumerate(data['faqs']):
            if faq['id'] == faq_id:
                # Update fields
                if question is not None:
                    data['faqs'][i]['question'] = question
                
                if answer is not None:
                    data['faqs'][i]['answer'] = answer
                
                if category is not None:
                    data['faqs'][i]['category'] = category
                    
                    # Add category if not exists
                    if category not in data['categories']:
                        data['categories'].append(category)
                
                # Update timestamp
                data['faqs'][i]['updated_at'] = datetime.now().isoformat()
                
                # Save data
                self._save_data(data)
                
                return data['faqs'][i]
        
        return None  # FAQ not found
    
    def delete_faq(self, faq_id: str) -> bool:
        """
        Delete an FAQ.
        
        Args:
            faq_id: The ID of the FAQ to delete
            
        Returns:
            True if deleted, False if not found
        """
        # Load FAQs
        data = self._load_data()
        
        # Find FAQ by ID
        for i, faq in enumerate(data['faqs']):
            if faq['id'] == faq_id:
                # Remove FAQ
                del data['faqs'][i]
                
                # Save data
                self._save_data(data)
                
                return True
        
        return False  # FAQ not found
    
    def get_faq(self, faq_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an FAQ by ID.
        
        Args:
            faq_id: The ID of the FAQ to get
            
        Returns:
            The FAQ dictionary or None if not found
        """
        # Load FAQs
        data = self._load_data()
        
        # Find FAQ by ID
        for faq in data['faqs']:
            if faq['id'] == faq_id:
                return faq
        
        return None  # FAQ not found
    
    def get_all_faqs(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all FAQs, optionally filtered by category.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of FAQ dictionaries
        """
        # Load FAQs
        data = self._load_data()
        
        # Filter by category if specified
        if category:
            return [faq for faq in data['faqs'] if faq['category'] == category]
        else:
            return data['faqs']
    
    def get_categories(self) -> List[str]:
        """
        Get all categories.
        
        Returns:
            List of category names
        """
        # Load FAQs
        data = self._load_data()
        
        return data['categories']
    
    def search_faqs(self, query: str) -> List[Dict[str, Any]]:
        """
        Search FAQs by query.
        
        Args:
            query: The search query
            
        Returns:
            List of matching FAQ dictionaries
        """
        # Load FAQs
        data = self._load_data()
        
        # Search for query in question and answer
        query = query.lower()
        return [
            faq for faq in data['faqs']
            if query in faq['question'].lower() or query in faq['answer'].lower()
        ]
    
    def _load_data(self) -> Dict[str, Any]:
        """Load FAQ data from file."""
        try:
            with open(self.faq_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {
                'faqs': [],
                'categories': []
            }
    
    def _save_data(self, data: Dict[str, Any]) -> None:
        """Save FAQ data to file."""
        with open(self.faq_file, 'w') as f:
            json.dump(data, f, indent=2)