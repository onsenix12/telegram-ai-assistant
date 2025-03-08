# src/error/error_handler.py content
from typing import Dict, Any, Optional, Callable
import traceback
import logging
from src.error.logger import get_logger

logger = get_logger(__name__)

class ErrorHandler:
    """Handle errors in the application."""
    
    def __init__(self):
        # Error response generators
        self.error_responses = {
            'default': lambda error, context: f"I'm sorry, something went wrong. Please try again later.",
            'not_found': lambda error, context: f"I couldn't find what you're looking for.",
            'auth_error': lambda error, context: f"You don't have permission to do that.",
            'validation_error': lambda error, context: f"There's an issue with your request: {str(error)}",
            'timeout': lambda error, context: f"The request timed out. Please try again later.",
            'api_error': lambda error, context: f"There was an issue connecting to the service. Please try again later.",
            'db_error': lambda error, context: f"There was a database error. Please try again later.",
            'parse_error': lambda error, context: f"I couldn't understand your request. Please try again with a different format."
        }
        
        # Error recovery handlers
        self.recovery_handlers = {
            'retry': self._retry_handler,
            'fallback': self._fallback_handler,
            'escalate': self._escalate_handler
        }
    
    def handle_error(self, error: Exception, error_type: str = 'default', 
                     context: Optional[Dict[str, Any]] = None, recovery_type: str = None) -> str:
        """
        Handle an error and return a user-friendly response.
        
        Args:
            error: The exception that occurred
            error_type: The type of error
            context: Additional context for error handling
            recovery_type: The type of recovery to attempt
            
        Returns:
            A user-friendly error message
        """
        # Log the error
        logger.error(f"Error occurred: {str(error)}")
        logger.error(traceback.format_exc())
        
        # Get error response generator
        response_generator = self.error_responses.get(error_type, self.error_responses['default'])
        
        # Generate user-friendly response
        user_response = response_generator(error, context or {})
        
        # Attempt recovery if specified
        if recovery_type and recovery_type in self.recovery_handlers:
            recovery_handler = self.recovery_handlers[recovery_type]
            recovery_result = recovery_handler(error, context or {})
            
            if recovery_result:
                user_response += f" {recovery_result}"
        
        return user_response
    
    def add_error_response(self, error_type: str, response_generator: Callable[[Exception, Dict[str, Any]], str]) -> None:
        """
        Add a custom error response generator.
        
        Args:
            error_type: The type of error
            response_generator: A function that generates a user-friendly response
        """
        self.error_responses[error_type] = response_generator
    
    def add_recovery_handler(self, recovery_type: str, recovery_handler: Callable[[Exception, Dict[str, Any]], Optional[str]]) -> None:
        """
        Add a custom recovery handler.
        
        Args:
            recovery_type: The type of recovery
            recovery_handler: A function that attempts to recover from an error
        """
        self.recovery_handlers[recovery_type] = recovery_handler
    
    def _retry_handler(self, error: Exception, context: Dict[str, Any]) -> Optional[str]:
        """Handle retry recovery."""
        max_retries = context.get('max_retries', 3)
        current_retry = context.get('current_retry', 0)
        
        if current_retry < max_retries:
            # In a real implementation, this would trigger a retry of the operation
            return "I'll try again for you."
        else:
            return "I've tried several times but still couldn't complete the operation."
    
    def _fallback_handler(self, error: Exception, context: Dict[str, Any]) -> Optional[str]:
        """Handle fallback recovery."""
        fallback_response = context.get('fallback_response')
        
        if fallback_response:
            return f"Instead, {fallback_response}"
        else:
            return None
    
    def _escalate_handler(self, error: Exception, context: Dict[str, Any]) -> Optional[str]:
        """Handle escalation recovery."""
        # In a real implementation, this would escalate the issue to a human operator
        return "I've notified a support team member who will look into this."