import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_claude_api():
    """Test direct communication with the Claude API."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("No ANTHROPIC_API_KEY found in environment variables!")
        return
    
    print(f"Using API key: {api_key[:4]}...{api_key[-4:]}")
    
    base_url = "https://api.anthropic.com/v1/messages"
    
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # Try multiple model names to find one that works
    model_names = [
        "claude-3-sonnet-20240229",
        "claude-3-opus-20240229",
        "claude-3-haiku-20240307",
        "claude-3-sonnet-20240307",
        "claude-3-opus-20240307",
        "claude-3-haiku",
        "claude-3-sonnet",
        "claude-3-opus",
        "claude-3",
        "claude-2",
        "claude-2.0",
        "claude-2.1",
        "claude-instant-1.2"
    ]
    
    for model_name in model_names:
        print(f"\n\n==== Testing with model: {model_name} ====")
        
        data = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": "What's the difference between cloud computing and artificial intelligence?"
                }
            ],
            "system": "You are an AI assistant for SMU Master's Program students.",
            "max_tokens": 1000
        }
        
        print(f"Sending request with model: {model_name}")
        
        try:
            response = requests.post(
                base_url,
                headers=headers,
                data=json.dumps(data)
            )
            
            print(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print("API call successful!")
                print(f"Response ID: {response_data.get('id', 'N/A')}")
                print(f"Model: {response_data.get('model', 'N/A')}")
                print(f"Content snippet: {response_data['content'][0]['text'][:100]}...")
                
                # If we found a working model, let's remember it
                with open("working_model.txt", "w") as f:
                    f.write(model_name)
                
                # Exit the loop after finding a working model
                break
            else:
                print(f"Error response: {response.text}")
        
        except Exception as e:
            print(f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    test_claude_api()