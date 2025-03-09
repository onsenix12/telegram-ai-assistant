import requests
import json

def test_auth_service():
    """Test the auth service endpoints."""
    print("Testing auth service...")
    
    try:
        # Test root endpoint
        response = requests.get("http://localhost:5050/")
        print(f"Root endpoint:")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text[:100]}...")
        
        # Test the status endpoint
        response = requests.get("http://localhost:5050/status")
        print(f"\nStatus endpoint:")
        print(f"Status code: {response.status_code}")
        status_data = json.loads(response.text)
        print(json.dumps(status_data, indent=2))
        
        # Test the verify endpoint
        response = requests.get("http://localhost:5050/verify/123456")
        print(f"\nVerify endpoint (for user 123456):")
        print(f"Status code: {response.status_code}")
        verify_data = json.loads(response.text)
        print(f"Authenticated: {verify_data.get('authenticated', False)}")
        print(f"User info: {verify_data.get('user_info')}")
        
        # Test the login/redirect URL
        login_url = "http://localhost:5050/login/123456"
        print(f"\nLogin URL: {login_url}")
        print("(This would redirect to Google OAuth, not testing the actual redirect)")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_auth_service()