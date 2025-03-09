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
    
    def send_message(self, user_message: str, conversation_history: Optional[List[Dict[str, Any]]] = None, custom_system_prompt: Optional[str] = None) -> str:
        """
        Send a message to Claude AI and get a response.
        
        Args:
            user_message: The user's message
            conversation_history: Optional list of previous messages in the conversation
            custom_system_prompt: Optional system prompt to override the default one
            
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
            "system": custom_system_prompt or self.system_prompt,
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
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Query knowledge base first
        knowledge_context = ""
        knowledge_found = False
        highest_score = 0
        
        try:
            import requests
            logger.info(f"Querying knowledge base with: {message[:50]}..." if len(message) > 50 else f"Querying knowledge base with: {message}")
            kb_response = requests.post(
                "http://knowledge-base:5000/search",
                json={"query": message},
                timeout=5
            )
            
            logger.info(f"Knowledge base response status: {kb_response.status_code}")
            
            if kb_response.status_code == 200:
                response_data = kb_response.json()
                logger.info(f"Knowledge base response data: {response_data}")
                results = response_data.get('results', [])
                knowledge_found = response_data.get('has_knowledge', False)
                highest_score = response_data.get('highest_score', 0)
                
                if results:
                    knowledge_context = "Here is some relevant information from SMU courses:\n\n"
                    for result in results:
                        # Check for 'content' field, fall back to 'text' field if not present
                        content = result.get('content', result.get('text', ''))
                        knowledge_context += f"--- {result['title']} ---\n{content}\n\n"
                    knowledge_context += "Please use this information to inform your response.\n\n"
        except Exception as e:
            # If knowledge base is not available, continue without it
            logger.error(f"Knowledge base query failed: {str(e)}")

        # If no relevant knowledge found or knowledge score is very low, return standard response
        if not knowledge_found or highest_score < 65:  # Lowered threshold to 65 to match search results
            logger.info(f"No relevant knowledge found (score: {highest_score}), checking if technical question")
            # Quick check if it's a programming or technical question (which Claude might know)
            programming_keywords = ['code', 'program', 'function', 'algorithm', 'python', 'java', 'javascript']
            is_technical_question = any(keyword in message.lower() for keyword in programming_keywords)
            
            # If it's not a technical question Claude would know, return the "not in knowledge" message
            if not is_technical_question:
                # Add this check before returning "not in knowledge" message
                # Basic conversational questions that shouldn't trigger the "not in knowledge" response
                basic_questions = [
                    'hello', 'hi', 'how are you', 'thank', 'goodbye', 'bye', 
                    'who are you', 'what can you do', 'help'
                ]

                is_basic_question = any(basic.lower() in message.lower() for basic in basic_questions)

                # If it's a basic question, continue with Claude's normal response
                if is_basic_question:
                    logger.info("Basic conversational question detected, processing normally")
                    # Process normally
                    pass
                else:
                    # Return the "not in knowledge" message for non-technical questions
                    logger.info("Non-technical question without knowledge base match, returning 'not in knowledge' message")
                    return "I don't have that in my knowledge."
        else:
            logger.info(f"Found relevant knowledge with score: {highest_score}. Knowledge will be used in response.")
        
        # Get conversation history from context
        conversation_history = context.get('claude_conversation', [])
        
        # Modify system prompt to include knowledge context
        enhanced_system_prompt = self.system_prompt
        if knowledge_context:
            logger.info("Adding knowledge context to system prompt")
            enhanced_system_prompt += f"\n\n{knowledge_context}"
        
        # Send message to Claude with enhanced system prompt
        response = self.send_message(message, conversation_history, enhanced_system_prompt)
        return response