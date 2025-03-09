import requests
import json
from src.nlp.Multi_part_Question_Handler import MultiPartQuestionHandler

def test_bot_auth_integration():
    """Test the bot's authentication integration."""
    print("Testing bot authentication integration...")
    
    # Create a test user ID
    test_user_id = "123456"
    
    # First check if the user is already authenticated via the auth service
    response = requests.get(f"http://localhost:5050/verify/{test_user_id}")
    verify_data = json.loads(response.text)
    
    print(f"Auth service verification for user {test_user_id}:")
    print(f"Authenticated: {verify_data.get('authenticated', False)}")
    print(f"User info: {verify_data.get('user_info')}")
    
    # Now test the bot's authentication check
    handler = MultiPartQuestionHandler()
    is_authenticated = handler._check_user_authenticated(test_user_id)
    
    print(f"\nBot authentication check for user {test_user_id}:")
    print(f"Authenticated: {is_authenticated}")
    
    # Test what happens when the user sends a message
    test_message = "Tell me about IS621"
    response = handler.process_message(test_user_id, test_message)
    
    print(f"\nBot response to message '{test_message}':")
    print(response)
    
    # Test with an unauthenticated user
    unauthenticated_user_id = "999999"
    response = handler.process_message(unauthenticated_user_id, test_message)
    
    print(f"\nBot response to unauthenticated user:")
    print(response)

if __name__ == "__main__":
    test_bot_auth_integration()