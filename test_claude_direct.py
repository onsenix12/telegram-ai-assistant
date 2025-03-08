import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from src.nlp.claude_integration import ClaudeAI

# Load environment variables
load_dotenv()

def main():
    """
    Test direct Claude API integration.
    This requires a valid ANTHROPIC_API_KEY in the .env file.
    """
    print("=== Testing Claude AI Integration Directly ===\n")
    
    # Create Claude AI instance
    try:
        claude = ClaudeAI()
        print("Successfully initialized Claude AI\n")
    except ValueError as e:
        print(f"Error initializing Claude AI: {str(e)}")
        return
    
    # Define test questions
    test_questions = [
        "What's the course content for IS623 AI and Machine Learning?",
        "Compare the workload and career prospects between IS622 Cloud Computing and IS623 AI courses.",
        "If I want to pursue a career in data science, which courses (IS621-IS625) should I prioritize and why?",
        "What's the difference between DevSecOps (IS621) and traditional software development approaches? How does this impact quality management (IS625)?",
    ]
    
    # Test each question
    user_id = "test_user_123"
    context = {}
    
    for i, question in enumerate(test_questions):
        print(f"Question {i+1}: {question}")
        
        # Process the question directly with Claude
        response = claude.handle_multi_part_question(user_id, question, context)
        
        # Print truncated response if it's too long
        if len(response) > 300:
            print(f"Response: {response[:300]}...\n(response truncated)")
        else:
            print(f"Response: {response}")
        
        print("-" * 70)
        print()
    
    print("Testing completed successfully!")

if __name__ == "__main__":
    main()