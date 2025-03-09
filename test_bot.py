import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.nlp.intent_classifier import IntentClassifier
from src.nlp.entity_extractor import EntityExtractor
from src.nlp.context_manager import ContextManager

def test_intent_classifier():
    print("\n--- Testing Intent Classifier ---")
    classifier = IntentClassifier()
    
    test_messages = [
        "Hello, how are you?",
        "Goodbye, talk to you later",
        "I need help with the IS623 course",
        "When is the deadline for the assignment?",
        "What materials do I need to study for the exam?",
        "What's my grade for IS624?",
        "What is the schedule for next week's classes?",
        "Can you provide the lecture notes for IS625?"
    ]
    
    for message in test_messages:
        intent, confidence = classifier.classify(message)
        print(f"Message: '{message}'")
        print(f"Intent: {intent}, Confidence: {confidence:.2f}")
        print()

def test_entity_extractor():
    print("\n--- Testing Entity Extractor ---")
    extractor = EntityExtractor()
    
    test_messages = [
        "I need information about IS623",
        "IS625 assignment due on 15/04/2025",
        "Meeting at 3:30PM for IS624",
        "Please contact me at student@smu.edu.sg",
        "I scored 85% in the last test",
        "I need to register for 3 courses"
    ]
    
    for message in test_messages:
        entities = extractor.extract_entities(message)
        print(f"Message: '{message}'")
        print(f"Entities: {entities}")
        print()

def test_context_manager():
    print("\n--- Testing Context Manager ---")
    context_mgr = ContextManager(expiry_seconds=30)  # Set short expiry for testing
    
    user_id = "12345"
    
    # Set initial context
    context_mgr.set_context(user_id, {"course": "IS623", "topic": "AI Models"})
    print(f"Initial context: {context_mgr.get_context(user_id)}")
    
    # Update context
    context_mgr.update_context(user_id, "assignment", "Project 2")
    print(f"Updated context: {context_mgr.get_context(user_id)}")
    
    # Clear context
    context_mgr.clear_context(user_id)
    print(f"After clearing: {context_mgr.get_context(user_id)}")

def main():
    print("=== Testing Telegram AI Assistant Components ===")
    
    test_intent_classifier()
    test_entity_extractor()
    test_context_manager()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main()

import unittest
from unittest.mock import MagicMock
from src.dialog.conversation_handler import ConversationHandler
from src.integrations.elearn.synchronizer import ELearnSynchronizer
import tempfile

class TestBotIntegration(unittest.TestCase):
    def test_conversation_flow(self):
        """Test a conversation flow."""
        # Initialize components
        conversation_handler = ConversationHandler()

        # User ID for the test
        user_id = "test_user"

        # First message: greeting
response = conversation_handler.process_message(user_id, "Hello")
assert isinstance(response, str)  # Just check if it's a string
# Or if you want to check the content:
assert "response" in response

class TestELearnIntegration(unittest.TestCase):
    def test_elearn_synchronization(self):
        """Test E-Learn synchronization."""
        with tempfile.TemporaryDirectory() as temp_data_dir:
            # Initialize synchronizer with temporary data directory and dummy mode
            synchronizer = ELearnSynchronizer(data_dir=temp_data_dir, dummy_mode=True)

            # Perform synchronization
            result = synchronizer.sync_all()

            # Assert that synchronization was successful
            assert result["courses_synced"] > 0
            assert result["materials_synced"] > 0
            assert result["assignments_synced"] > 0
            assert result["schedule_synced"] > 0

if __name__ == '__main__':
    unittest.main()