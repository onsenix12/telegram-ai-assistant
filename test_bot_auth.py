import requests
import json
import os
import time
from src.nlp.Multi_part_Question_Handler import MultiPartQuestionHandler

def test_bot_auth_integration():
    """Test the bot's authentication integration."""
    print("Testing bot authentication integration...")
    
    # Create a test user ID
    test_user_id = "123456"
    unauthenticated_user_id = "999999"
    
    # First check if the authenticated user exists, if not create it
    response = requests.get(f"http://localhost:5050/verify/{test_user_id}")
    verify_data = json.loads(response.text)
    
    print(f"Auth service verification for user {test_user_id}:")
    print(f"Authenticated: {verify_data.get('authenticated', False)}")
    
    if not verify_data.get('authenticated', False):
        print(f"Adding test user {test_user_id}...")
        test_user = {
            "email": "test.user@smu.edu.sg",
            "name": "Test User",
            "authenticated_at": "2025-03-09T14:30:00"
        }
        
        response = requests.post(
            f"http://localhost:5050/dev/add_test_user/{test_user_id}",
            json=test_user
        )
        
        if response.status_code == 201:
            print(f"Test user {test_user_id} added successfully")
        else:
            print(f"Failed to add test user: {response.text}")
        
        # Wait a moment for the database to update
        time.sleep(1)
    
    # Now test the bot's authentication check
    handler = MultiPartQuestionHandler()
    
    # Set DEV_MODE environment variable temporarily
    os.environ['DEV_MODE'] = 'true'
    
    is_authenticated = handler._check_user_authenticated(test_user_id)
    print(f"\nBot authentication check for user {test_user_id}:")
    print(f"Authenticated: {is_authenticated}")
    
    # Test what happens when the user sends a message
    test_message = "Tell me about IS621"
    response = handler.process_message(test_user_id, test_message)
    
    print(f"\nBot response to message '{test_message}':")
    print(response)
    
    # Test with an unauthenticated user
    response = handler.process_message(unauthenticated_user_id, test_message)
    
    print(f"\nBot response to unauthenticated user:")
    print(response)
    
    # Clean up environment variable
    del os.environ['DEV_MODE']
    
    print("\nTesting without DEV_MODE:")
    # Now test without DEV_MODE to see the actual authentication behavior
    is_authenticated = handler._check_user_authenticated(test_user_id)
    print(f"Authenticated user check: {is_authenticated}")
    
    is_authenticated = handler._check_user_authenticated(unauthenticated_user_id)
    print(f"Unauthenticated user check: {is_authenticated}")

if __name__ == "__main__":
    test_bot_auth_integration()