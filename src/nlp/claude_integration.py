import os
import requests
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ClaudeAI:
    """Integration with Claude AI for handling complex queries."""
    
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")
        
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-opus-20240229"  # Updated to working model name
        self.max_tokens = 1000
        
        # System prompt to guide Claude's responses
        self.system_prompt = """
        You are an AI assistant for SMU Master's Program students. Your role is to provide helpful, 
        accurate information about courses, assignments, and learning materials.
        
        Focus on providing educational guidance and support. Keep your responses concise, 
        informative, and tailored to academic contexts. 
        
        When you don't know specific information about SMU programs, you should indicate this 
        clearly rather than making up information.
        
        For course-specific queries, you have knowledge about the following courses:
        - IS621: Agile and DevSecOps
        - IS622: Cloud Computing and Container Architecture  
        - IS623: AI and Machine Learning
        - IS624: Big Data and Analytics
        - IS625: Software Quality Management
        """
    
    def send_message(self, user_message: str, conversation_history: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Send a message to Claude AI and get a response.
        
        Args:
            user_message: The user's message
            conversation_history: Optional list of previous messages in the conversation
            
        Returns:
            Claude's response text
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Sending message to Claude: {user_message[:50]}..." if len(user_message) > 50 else f"Sending message to Claude: {user_message}")
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        # Prepare messages
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add the current user message
        messages.append({"role": "user", "content": user_message})
        
        # Prepare the request data
        data = {
            "model": self.model,
            "messages": messages,
            "system": self.system_prompt,
            "max_tokens": self.max_tokens
        }
        
        try:
            logger.info(f"Using Claude model: {self.model}")
            response = requests.post(
                self.base_url,
                headers=headers,
                data=json.dumps(data),
                timeout=30  # Add timeout
            )
            
            logger.info(f"Claude API response status code: {response.status_code}")
            
            response.raise_for_status()  # Raise exception for HTTP errors
            
            response_data = response.json()
            response_text = response_data["content"][0]["text"]
            logger.info(f"Claude API response received: {response_text[:50]}..." if len(response_text) > 50 else f"Claude API response received: {response_text}")
            return response_text
        
        except requests.exceptions.Timeout:
            error_message = "Timeout while communicating with Claude API"
            logger.error(error_message)
            return f"I'm currently experiencing delays. Please try again in a moment."
            
        except requests.exceptions.RequestException as e:
            error_message = f"Error communicating with Claude API: {str(e)}"
            response = getattr(e, 'response', None)
            if response:
                error_message += f"\nResponse: {response.text}"
            # Log the error
            logger.error(f"Claude API Error: {error_message}")
            return f"I'm currently having trouble answering complex questions. Please try a simpler question or try again later."
            
        except Exception as e:
            logger.error(f"Unexpected error in Claude API communication: {str(e)}")
            return f"I encountered an unexpected error. Please try again with a different question."
    
    def handle_multi_part_question(self, user_id: str, message: str, context: Dict[str, Any]) -> str:
        """
        Handle a complex multi-part question using Claude AI.
        
        Args:
            user_id: The unique identifier for the user
            message: The user's message
            context: The conversation context
            
        Returns:
            The response text
        """
        # Get conversation history from context
        conversation_history = context.get('claude_conversation', [])
        
        # Send message to Claude
        response = self.send_message(message, conversation_history)
        
        # Update conversation history
        conversation_history.append({"role": "user", "content": message})
        conversation_history.append({"role": "assistant", "content": response})
        
        # Limit conversation history to last 10 messages to avoid context overflow
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
        
        # Update context with new conversation history
        context['claude_conversation'] = conversation_history
        
        return response