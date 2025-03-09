import requests
import json
import time

def test_mock_user_auth():
    """Mock a user authentication for testing purposes."""
    print("Adding a mock authenticated user to the auth service...")
    
    try:
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
        
        # Wait a moment for the database to update
        time.sleep(1)
        
        # Check if the user is authenticated
        response = requests.get(f"http://localhost:5050/verify/{test_user_id}")
        verify_data = json.loads(response.text)
        print(f"\nCurrently, user {test_user_id} authenticated = {verify_data.get('authenticated', False)}")
        if verify_data.get('authenticated', False):
            print("User info:")
            print(json.dumps(verify_data.get('user_info', {}), indent=2))
        
        # Check the status endpoint to see the user count
        response = requests.get("http://localhost:5050/status")
        status_data = json.loads(response.text)
        print(f"\nUser count in database: {status_data.get('authenticated_users', 0)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_mock_user_auth()