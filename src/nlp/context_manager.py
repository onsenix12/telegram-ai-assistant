# src/nlp/context_manager.py content
from typing import Dict, Any, Optional
import time

class ContextManager:
    """Manage conversation context for multi-turn dialogues."""
    
    def __init__(self, expiry_seconds: int = 600):
        # Dictionary to store user contexts
        self.contexts = {}
        self.expiry_seconds = expiry_seconds  # Context expiry time in seconds
    
    def set_context(self, user_id: str, context_data: Dict[str, Any]) -> None:
        """
        Set context for a user.
        
        Args:
            user_id: The unique identifier for the user
            context_data: The context data to store
        """
        # Create or update user context
        if user_id not in self.contexts:
            self.contexts[user_id] = {}
        
        # Update with new data
        self.contexts[user_id].update(context_data)
        
        # Set last updated time
        self.contexts[user_id]['_last_updated'] = time.time()
    
    def get_context(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get context for a user.
        
        Args:
            user_id: The unique identifier for the user
            
        Returns:
            The user's context data or None if expired/not found
        """
        # Check if user has a context
        if user_id not in self.contexts:
            return None
        
        # Check if context has expired
        last_updated = self.contexts[user_id].get('_last_updated', 0)
        if time.time() - last_updated > self.expiry_seconds:
            self.clear_context(user_id)
            return None
        
        # Return user context without internal fields
        context = self.contexts[user_id].copy()
        internal_fields = [key for key in context if key.startswith('_')]
        for field in internal_fields:
            context.pop(field)
        
        return context
    
    def update_context(self, user_id: str, key: str, value: Any) -> None:
        """
        Update a specific key in the user's context.
        
        Args:
            user_id: The unique identifier for the user
            key: The context key to update
            value: The new value for the key
        """
        if user_id in self.contexts:
            self.contexts[user_id][key] = value
            self.contexts[user_id]['_last_updated'] = time.time()
    
    def clear_context(self, user_id: str) -> None:
        """
        Clear context for a user.
        
        Args:
            user_id: The unique identifier for the user
        """
        if user_id in self.contexts:
            del self.contexts[user_id]