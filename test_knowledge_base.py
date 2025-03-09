import requests
import json

def test_knowledge_base():
    """Test the knowledge base search functionality."""
    print("Testing knowledge base...")
    
    try:
        response = requests.post(
            "http://localhost:5000/search",
            json={"query": "What is DevSecOps?"},
            timeout=5
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_knowledge_base()