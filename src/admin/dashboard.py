# src/admin/dashboard.py content
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime

class Dashboard:
    """Admin dashboard for the AI Learning Assistant."""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize counters file if not exists
        counters_file = os.path.join(data_dir, 'counters.json')
        if not os.path.exists(counters_file):
            with open(counters_file, 'w') as f:
                json.dump({
                    'total_messages': 0,
                    'total_users': 0,
                    'total_conversations': 0,
                    'intents': {}
                }, f)
    
    def update_counters(self, user_id: str, message: str, intent: str) -> None:
        """
        Update usage counters.
        
        Args:
            user_id: The unique identifier for the user
            message: The user's message
            intent: The detected intent
        """
        # Load counters
        counters = self._load_counters()
        
        # Update message count
        counters['total_messages'] += 1
        
        # Update user count if new user
        user_file = os.path.join(self.data_dir, f'user_{user_id}.json')
        if not os.path.exists(user_file):
            counters['total_users'] += 1
        
        # Update intent counts
        if intent not in counters['intents']:
            counters['intents'][intent] = 0
        counters['intents'][intent] += 1
        
        # Save counters
        self._save_counters(counters)
    
    def record_conversation(self, user_id: str, messages: List[Dict[str, Any]]) -> None:
        """
        Record a conversation.
        
        Args:
            user_id: The unique identifier for the user
            messages: List of message dictionaries with 'sender', 'text', and 'timestamp' keys
        """
        # Load counters
        counters = self._load_counters()
        
        # Update conversation count
        counters['total_conversations'] += 1
        
        # Save counters
        self._save_counters(counters)
        
        # Save conversation
        conversation_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        conversation_file = os.path.join(self.data_dir, f'conversation_{conversation_id}.json')
        
        with open(conversation_file, 'w') as f:
            json.dump({
                'user_id': user_id,
                'conversation_id': conversation_id,
                'timestamp': datetime.now().isoformat(),
                'messages': messages
            }, f)
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """
        Get usage statistics.
        
        Returns:
            Dictionary of usage statistics
        """
        # Load counters
        counters = self._load_counters()
        
        # Get list of users
        users = []
        for file in os.listdir(self.data_dir):
            if file.startswith('user_') and file.endswith('.json'):
                users.append(file[5:-5])  # Extract user ID from filename
        
        # Create statistics dictionary
        return {
            'message_count': counters['total_messages'],
            'user_count': counters['total_users'],
            'conversation_count': counters['total_conversations'],
            'intent_distribution': counters['intents'],
            'active_users': len(users)
        }
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversations.
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversation data
        """
        conversations = []
        
        # Get conversation files
        for file in os.listdir(self.data_dir):
            if file.startswith('conversation_') and file.endswith('.json'):
                file_path = os.path.join(self.data_dir, file)
                
                try:
                    with open(file_path, 'r') as f:
                        conversation = json.load(f)
                        conversations.append(conversation)
                except json.JSONDecodeError:
                    pass
        
        # Sort by timestamp (descending)
        conversations.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Return limited number of conversations
        return conversations[:limit]
    
    def search_conversations(self, query: str) -> List[Dict[str, Any]]:
        """
        Search conversations.
        
        Args:
            query: Search query
            
        Returns:
            List of matching conversation data
        """
        results = []
        
        # Get conversation files
        for file in os.listdir(self.data_dir):
            if file.startswith('conversation_') and file.endswith('.json'):
                file_path = os.path.join(self.data_dir, file)
                
                try:
                    with open(file_path, 'r') as f:
                        conversation = json.load(f)
                        
                        # Check if any message contains the query
                        for message in conversation.get('messages', []):
                            if query.lower() in message.get('text', '').lower():
                                results.append(conversation)
                                break
                except json.JSONDecodeError:
                    pass
        
        # Sort by timestamp (descending)
        results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return results
    
    def _load_counters(self) -> Dict[str, Any]:
        """Load counters from file."""
        counters_file = os.path.join(self.data_dir, 'counters.json')
        
        try:
            with open(counters_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {
                'total_messages': 0,
                'total_users': 0,
                'total_conversations': 0,
                'intents': {}
            }
    
    def _save_counters(self, counters: Dict[str, Any]) -> None:
        """Save counters to file."""
        counters_file = os.path.join(self.data_dir, 'counters.json')
        
        with open(counters_file, 'w') as f:
            json.dump(counters, f, indent=2)