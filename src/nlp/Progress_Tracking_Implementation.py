# src/tracking/progress_tracker.py content
from typing import Dict, List, Any
import json
import os
from datetime import datetime

class ProgressTracker:
    """Track student learning progress."""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
    
    def record_interaction(self, user_id: str, course_code: str, topic: str, interaction_type: str) -> None:
        """
        Record a learning interaction.
        
        Args:
            user_id: The unique identifier for the user
            course_code: The course code (e.g., IS621)
            topic: The topic of the interaction
            interaction_type: The type of interaction (e.g., question, quiz, material_access)
        """
        # Load existing data
        user_data = self._load_user_data(user_id)
        
        # Initialize course data if not exists
        if course_code not in user_data:
            user_data[course_code] = {
                'interactions': [],
                'last_active': None,
                'topics': {}
            }
        
        # Initialize topic data if not exists
        if topic not in user_data[course_code]['topics']:
            user_data[course_code]['topics'][topic] = {
                'interaction_count': 0,
                'last_interaction': None
            }
        
        # Update interaction data
        timestamp = datetime.now().isoformat()
        
        # Add new interaction
        user_data[course_code]['interactions'].append({
            'timestamp': timestamp,
            'topic': topic,
            'type': interaction_type
        })
        
        # Update topic statistics
        user_data[course_code]['topics'][topic]['interaction_count'] += 1
        user_data[course_code]['topics'][topic]['last_interaction'] = timestamp
        
        # Update course last active time
        user_data[course_code]['last_active'] = timestamp
        
        # Save data
        self._save_user_data(user_id, user_data)
    
    def get_user_progress(self, user_id: str, course_code: str = None) -> Dict[str, Any]:
        """
        Get progress data for a user.
        
        Args:
            user_id: The unique identifier for the user
            course_code: Optional course code to filter by
            
        Returns:
            Progress data for the user
        """
        # Load user data
        user_data = self._load_user_data(user_id)
        
        if course_code:
            # Return data for specific course
            return user_data.get(course_code, {})
        else:
            # Return summary for all courses
            summary = {}
            
            for code, data in user_data.items():
                topic_count = len(data.get('topics', {}))
                interaction_count = len(data.get('interactions', []))
                last_active = data.get('last_active')
                
                summary[code] = {
                    'topic_count': topic_count,
                    'interaction_count': interaction_count,
                    'last_active': last_active
                }
            
            return summary
    
    def get_active_topics(self, user_id: str, course_code: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most active topics for a user in a course.
        
        Args:
            user_id: The unique identifier for the user
            course_code: The course code
            limit: Maximum number of topics to return
            
        Returns:
            List of topic data sorted by interaction count
        """
        # Load user data
        user_data = self._load_user_data(user_id)
        
        # Get course data
        course_data = user_data.get(course_code, {})
        topics_data = course_data.get('topics', {})
        
        # Convert to list and sort by interaction count
        topics_list = [
            {
                'name': name,
                'interaction_count': data['interaction_count'],
                'last_interaction': data['last_interaction']
            }
            for name, data in topics_data.items()
        ]
        
        # Sort by interaction count (descending)
        topics_list.sort(key=lambda x: x['interaction_count'], reverse=True)
        
        # Return limited number of topics
        return topics_list[:limit]
    
    def _load_user_data(self, user_id: str) -> Dict[str, Any]:
        """Load user data from file."""
        file_path = os.path.join(self.data_dir, f'user_{user_id}.json')
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        else:
            return {}
    
    def _save_user_data(self, user_id: str, data: Dict[str, Any]) -> None:
        """Save user data to file."""
        file_path = os.path.join(self.data_dir, f'user_{user_id}.json')
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)