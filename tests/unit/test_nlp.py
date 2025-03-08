# tests/unit/test_nlp.py content
from src.nlp.intent_classifier import IntentClassifier
from src.nlp.entity_extractor import EntityExtractor
from src.nlp.context_manager import ContextManager

class TestIntentClassifier:
    """Test the intent classifier."""
    
    def test_classify(self):
        """Test intent classification."""
        classifier = IntentClassifier()
        
        # Test greeting intent
        intent, confidence = classifier.classify("Hello there")
        assert intent == "greeting"
        assert confidence > 0
        
        # Test farewell intent
        intent, confidence = classifier.classify("Goodbye, see you later")
        assert intent == "farewell"
        assert confidence > 0
        
        # Test course info intent
        intent, confidence = classifier.classify("Tell me about course IS621")
        assert intent == "course_info"
        assert confidence > 0
        
        # Test unknown intent
        intent, confidence = classifier.classify("xyzabc")
        assert intent == "unknown"
        assert confidence == 0
    
    def test_get_all_scores(self):
        """Test getting all intent scores."""
        classifier = IntentClassifier()
        
        # Test multiple intents
        scores = classifier.get_all_scores("Can you help me with the IS621 course assignment?")
        
        # Both 'help' and 'course_info' should have scores
        assert scores["help"] > 0
        assert scores["course_info"] > 0
        assert scores["assignment"] > 0

class TestEntityExtractor:
    """Test the entity extractor."""
    
    def test_extract_entities(self):
        """Test entity extraction."""
        extractor = EntityExtractor()
        
        # Test course code extraction
        entities = extractor.extract_entities("I need info about IS621")
        assert "course_code" in entities
        assert "621" in entities["course_code"]
        
        # Test date extraction
        entities = extractor.extract_entities("The assignment is due on 10/15/2023")
        assert "date" in entities
        assert "10/15/2023" in entities["date"]
        
        # Test time extraction
        entities = extractor.extract_entities("The class starts at 2:30pm")
        assert "time" in entities
        assert "2:30pm" in entities["time"]
        
        # Test multiple entities
        entities = extractor.extract_entities("IS621 class on 9/1/2023 at 10:00am")
        assert "course_code" in entities
        assert "date" in entities
        assert "time" in entities

class TestContextManager:
    """Test the context manager."""
    
    def test_context_lifecycle(self):
        """Test setting, getting, and clearing context."""
        context_manager = ContextManager(expiry_seconds=10)
        user_id = "test_user"
        
        # Set context
        context_manager.set_context(user_id, {"key1": "value1", "key2": "value2"})
        
        # Get context
        context = context_manager.get_context(user_id)
        assert context is not None
        assert context["key1"] == "value1"
        assert context["key2"] == "value2"
        
        # Update context
        context_manager.update_context(user_id, "key1", "new_value")
        context = context_manager.get_context(user_id)
        assert context["key1"] == "new_value"
        
        # Clear context
        context_manager.clear_context(user_id)
        context = context_manager.get_context(user_id)
        assert context is None