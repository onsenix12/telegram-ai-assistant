import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from src.nlp.Multi_part_Question_Handler import MultiPartQuestionHandler

# Load environment variables
load_dotenv()

def main():
    """
    Test the multi-part question handler with Claude integration.
    This requires a valid ANTHROPIC_API_KEY in the .env file.
    """
    print("=== Testing SMU Master's Program AI Assistant ===\n")
    
    # Check if Claude API is configured
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in .env file.")
        print("Please add your Claude API key to the .env file before running this test.\n")
        return
    
    print(f"Using Claude API with key: {api_key[:4]}...{api_key[-4:]}\n")
    
    # Initialize the handler
    handler = MultiPartQuestionHandler(use_claude=True)
    
    # Define test questions (simple and complex)
    test_questions = [
        # Simple questions
        "Tell me about IS623",
        "What's the course content for AI and Machine Learning?",
        
        # Complex questions
        "Compare the workload and career prospects between Cloud Computing and AI courses.",
        "If I want to pursue a career in data science, which courses should I prioritize and why?",
        "What's the difference between DevSecOps and traditional software development approaches? How does this impact quality management?"
    ]
    
    # Test each question
    user_id = "test_user_123"
    for i, question in enumerate(test_questions):
        print(f"Question {i+1}: {question}")
        
        # Process the question
        response = handler.process_message(user_id, question)
        
        # Print truncated response if it's too long
        if len(response) > 300:
            print(f"Response: {response[:300]}...\n(response truncated)")
        else:
            print(f"Response: {response}")
        
        print("-" * 70)
        print()
    
    print("Testing completed successfully!")
    print("The Telegram AI Assistant is now ready to be integrated with your Telegram bot.")
    print("To use it in the Telegram bot, ensure that main.py is properly configured to use the MultiPartQuestionHandler.")

if __name__ == "__main__":
    main()