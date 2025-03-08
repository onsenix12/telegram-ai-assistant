# src/monitoring/metrics.py content
from typing import Dict, Any, List, Optional
import time
import os
import json
from datetime import datetime
import threading
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collect and store performance metrics."""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.metrics_file = os.path.join(data_dir, 'metrics.json')
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize metrics file if not exists
        if not os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'w') as f:
                json.dump({
                    'response_times': [],
                    'api_calls': [],
                    'error_counts': {},
                    'user_counts': {},
                    'message_counts': {}
                }, f)
        
        # Lock for thread-safe access
        self.lock = threading.Lock()
    
    def record_response_time(self, operation: str, duration_ms: float) -> None:
        """
        Record a response time metric.
        
        Args:
            operation: The name of the operation
            duration_ms: The duration in milliseconds
        """
        with self.lock:
            # Load metrics
            metrics = self._load_metrics()
            
            # Add new response time
            metrics['response_times'].append({
                'timestamp': datetime.now().isoformat(),
                'operation': operation,
                'duration_ms': duration_ms
            })
            
            # Keep only the most recent 1000 response times
            if len(metrics['response_times']) > 1000:
                metrics['response_times'] = metrics['response_times'][-1000:]
            
            # Save metrics
            self._save_metrics(metrics)
    
    def record_api_call(self, api: str, endpoint: str, status_code: int, duration_ms: float) -> None:
        """
        Record an API call metric.
        
        Args:
            api: The name of the API
            endpoint: The API endpoint
            status_code: The HTTP status code
            duration_ms: The duration in milliseconds
        """
        with self.lock:
            # Load metrics
            metrics = self._load_metrics()
            
            # Add new API call
            metrics['api_calls'].append({
                'timestamp': datetime.now().isoformat(),
                'api': api,
                'endpoint': endpoint,
                'status_code': status_code,
                'duration_ms': duration_ms
            })
            
            # Keep only the most recent 1000 API calls
            if len(metrics['api_calls']) > 1000:
                metrics['api_calls'] = metrics['api_calls'][-1000:]
            
            # Save metrics
            self._save_metrics(metrics)
    
    def record_error(self, error_type: str) -> None:
        """
        Record an error metric.
        
        Args:
            error_type: The type of error
        """
        with self.lock:
            # Load metrics
            metrics = self._load_metrics()
            
            # Initialize error count if not exists
            if error_type not in metrics['error_counts']:
                metrics['error_counts'][error_type] = 0
            
            # Increment error count
            metrics['error_counts'][error_type] += 1
            
            # Save metrics
            self._save_metrics(metrics)
    
    def record_user_activity(self, user_id: str) -> None:
        """
        Record user activity.
        
        Args:
            user_id: The user ID
        """
        with self.lock:
            # Load metrics
            metrics = self._load_metrics()
            
            # Get current date
            date = datetime.now().strftime('%Y-%m-%d')
            
            # Initialize user count for date if not exists
            if date not in metrics['user_counts']:
                metrics['user_counts'][date] = {'total': 0, 'users': []}
            
            # Add user to set for the current date if not already recorded
            if user_id not in metrics['user_counts'][date]['users']:
                metrics['user_counts'][date]['users'].append(user_id)
                metrics['user_counts'][date]['total'] += 1
            
            # Save metrics
            self._save_metrics(metrics)
    
    def record_message(self, message_type: str) -> None:
        """
        Record a message metric.
        
        Args:
            message_type: The type of message (e.g., 'user', 'bot')
        """
        with self.lock:
            # Load metrics
            metrics = self._load_metrics()
            
            # Get current date
            date = datetime.now().strftime('%Y-%m-%d')
            
            # Initialize message count for date if not exists
            if date not in metrics['message_counts']:
                metrics['message_counts'][date] = {}
            
            # Initialize message type count if not exists
            if message_type not in metrics['message_counts'][date]:
                metrics['message_counts'][date][message_type] = 0
            
            # Increment message count
            metrics['message_counts'][date][message_type] += 1
            
            # Save metrics
            self._save_metrics(metrics)
    
    def get_average_response_time(self, operation: Optional[str] = None, 
                                  time_window_minutes: int = 60) -> float:
        """
        Get average response time for an operation.
        
        Args:
            operation: Optional operation to filter by
            time_window_minutes: Time window in minutes
            
        Returns:
            Average response time in milliseconds
        """
        # Load metrics
        metrics = self._load_metrics()
        
        # Get current time
        now = datetime.now()
        
        # Filter response times by time window and operation
        filtered_times = []
        for item in metrics['response_times']:
            try:
                # Parse timestamp
                timestamp = datetime.fromisoformat(item['timestamp'])
                
                # Check if within time window
                if (now - timestamp).total_seconds() <= time_window_minutes * 60:
                    # Check operation if specified
                    if operation is None or item['operation'] == operation:
                        filtered_times.append(item['duration_ms'])
            except (ValueError, KeyError):
                pass
        
        # Calculate average
        if filtered_times:
            return sum(filtered_times) / len(filtered_times)
        else:
            return 0
    
    def get_error_rate(self, time_window_minutes: int = 60) -> Dict[str, float]:
        """
        Get error rate.
        
        Args:
            time_window_minutes: Time window in minutes
            
        Returns:
            Dictionary mapping error types to rates
        """
        # Load metrics
        metrics = self._load_metrics()
        
        # Get current time
        now = datetime.now()
        
        # Filter API calls by time window
        total_calls = 0
        error_calls = 0
        
        for item in metrics['api_calls']:
            try:
                # Parse timestamp
                timestamp = datetime.fromisoformat(item['timestamp'])
                
                # Check if within time window
                if (now - timestamp).total_seconds() <= time_window_minutes * 60:
                    total_calls += 1
                    
                    # Check if error (status code >= 400)
                    if item['status_code'] >= 400:
                        error_calls += 1
            except (ValueError, KeyError):
                pass
        
        # Calculate error rate
        if total_calls > 0:
            return {'total_rate': error_calls / total_calls}
        else:
            return {'total_rate': 0}
    
    def get_user_count(self, date: Optional[str] = None) -> int:
        """
        Get user count for a date.
        
        Args:
            date: Optional date string (YYYY-MM-DD)
            
        Returns:
            Number of users
        """
        # Load metrics
        metrics = self._load_metrics()
        
        # Use current date if not specified
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Get user count for date
        if date in metrics['user_counts']:
            return metrics['user_counts'][date]['total']
        else:
            return 0
    
    def get_message_count(self, date: Optional[str] = None, 
                           message_type: Optional[str] = None) -> int:
        """
        Get message count for a date and type.
        
        Args:
            date: Optional date string (YYYY-MM-DD)
            message_type: Optional message type
            
        Returns:
            Number of messages
        """
        # Load metrics
        metrics = self._load_metrics()
        
        # Use current date if not specified
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Get message count for date and type
        if date in metrics['message_counts']:
            if message_type is None:
                # Sum all message types
                return sum(metrics['message_counts'][date].values())
            elif message_type in metrics['message_counts'][date]:
                return metrics['message_counts'][date][message_type]
        
        return 0
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all metrics.
        
        Returns:
            Dictionary with metrics summary
        """
        # Load metrics
        metrics = self._load_metrics()
        
        # Current date
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Calculate summary
        summary = {
            'average_response_time_ms': self.get_average_response_time(),
            'error_rate': self.get_error_rate()['total_rate'],
            'active_users_today': self.get_user_count(today),
            'messages_today': self.get_message_count(today),
            'top_errors': sorted(
                metrics['error_counts'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
        
        return summary
    
    def _load_metrics(self) -> Dict[str, Any]:
        """Load metrics from file."""
        try:
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {
                'response_times': [],
                'api_calls': [],
                'error_counts': {},
                'user_counts': {},
                'message_counts': {}
            }
    
    def _save_metrics(self, metrics: Dict[str, Any]) -> None:
        """Save metrics to file."""
        with open(self.metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)