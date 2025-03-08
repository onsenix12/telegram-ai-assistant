from datetime import datetime

class User:
    """User model for storing user data."""
    
    def __init__(self, user_id, first_name, username=None):
        self.user_id = user_id
        self.first_name = first_name
        self.username = username
        self.created_at = datetime.now()
        self.last_active = datetime.now()
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'user_id': self.user_id,
            'first_name': self.first_name,
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat()
        }

class Interaction:
    """Model for storing user interactions."""
    
    def __init__(self, user_id, message, intent, entities=None):
        self.user_id = user_id
        self.message = message
        self.intent = intent
        self.entities = entities or {}
        self.timestamp = datetime.now()
    
    def to_dict(self):
        """Convert interaction to dictionary."""
        return {
            'user_id': self.user_id,
            'message': self.message,
            'intent': self.intent,
            'entities': self.entities,
            'timestamp': self.timestamp.isoformat()
        }