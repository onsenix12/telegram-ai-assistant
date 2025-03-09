import requests
import json

def test_mock_user_auth():
    """Mock a user authentication for testing purposes."""
    print("Adding a mock authenticated user to the auth service...")
    
    try:
        # We'd usually do this through the OAuth flow, but we'll mock it for testing
        # by making a direct API request to add a user to the authenticated_users dictionary
        
        # First, define a test user
        test_user_id = "123456"
        test_user = {
            "email": "test.user@smu.edu.sg",
            "name": "Test User",
            "authenticated_at": "2025-03-09T14:30:00"
        }
        
        # Use our development endpoint to add the test user
        print(f"Adding user {test_user_id} with data:")
        print(json.dumps(test_user, indent=2))
        
        response = requests.post(
            f"http://localhost:5050/dev/add_test_user/{test_user_id}",
            json=test_user
        )
        
        print(f"\nAdd user response (status {response.status_code}):")
        print(json.dumps(response.json(), indent=2))
        
        # Check if the user would be authenticated
        response = requests.get(f"http://localhost:5050/verify/{test_user_id}")
        verify_data = json.loads(response.text)
        print(f"\nCurrently, user {test_user_id} authenticated = {verify_data.get('authenticated', False)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_mock_user_auth()