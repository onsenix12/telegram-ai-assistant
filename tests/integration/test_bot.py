# tests/integration/test_bot.py content
from src.nlp.intent_classifier import IntentClassifier
from src.nlp.entity_extractor import EntityExtractor
from src.nlp.context_manager import ContextManager
from src.dialog.conversation_handler import ConversationHandler

class TestBotIntegration:
    """Test the bot's components working together."""
    
    def test_conversation_flow(self):
        """Test a conversation flow."""
        # Initialize components
        conversation_handler = ConversationHandler()
        
        # User ID for the test
        user_id = "test_user"
        
        # First message: greeting
        response = conversation_handler.process_message(user_id, "Hello")
        assert "intent" in response
        assert response["intent"] == "greeting"
        assert "Hello! How can I assist you today?" in response["message"]
        
        # Second message: course info request
        response = conversation_handler.process_message(user_id, "Tell me about IS621")
        assert "intent" in response
        assert response["intent"] == "course_info"
        assert "IS621 is about Agile and DevSecOps." in response["message"]
        
        # Third message: assignment inquiry
        response = conversation_handler.process_message(user_id, "What assignments are due for IS621?")
        assert "intent" in response
        assert response["intent"] == "assignment_inquiry"
        assert "The following assignments are due for IS621:" in response["message"]
        
        # Fourth message: learning materials
        response = conversation_handler.process_message(user_id, "Show me learning materials for IS621")
        assert "intent" in response
        assert response["intent"] == "learning_materials"
        assert "Here are the learning materials for IS621:" in response["message"]

class TestELearnIntegration:
    """Test integration with SMU E-Learn."""
    
    def test_elearn_synchronization(self, temp_data_dir):
        """Test E-Learn synchronization."""
        from src.integrations.elearn.synchronizer import ELearnSynchronizer
        
        # Initialize synchronizer with temporary data directory
        synchronizer = ELearnSynchronizer(data_dir=temp_data_dir)
        
        # Sync course
        result = synchronizer.sync_course("IS621")
        
        # Check sync result
        assert result["course_synced"] == True
        assert result["materials_synced"] > 0
        assert result["assignments_synced"] > 0
        assert result["schedule_synced"] > 0
        
        # Get course data
        course = synchronizer.get_course("IS621")
        assert course is not None
        assert course["code"] == "IS621"
        
        # Get course materials
        materials = synchronizer.get_course_materials("IS621")
        assert len(materials) > 0
        
        # Get course assignments
        assignments = synchronizer.get_course_assignments("IS621")
        assert len(assignments) > 0
        
        # Get course schedule
        schedule = synchronizer.get_course_schedule("IS621")
        assert len(schedule) > 0