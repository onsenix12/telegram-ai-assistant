# tests/conftest.py content
import pytest
import os
import shutil
import tempfile

@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for testing."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Yield the directory path
    yield temp_dir
    
    # Clean up after test
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_telegram_update():
    """Create a mock Telegram update object for testing."""
    class MockUser:
        def __init__(self, id, first_name):
            self.id = id
            self.first_name = first_name
    
    class MockChat:
        def __init__(self, id):
            self.id = id
    
    class MockMessage:
        def __init__(self, message_id, text, user_id, first_name, chat_id):
            self.message_id = message_id
            self.text = text
            self.from_user = MockUser(user_id, first_name)
            self.chat = MockChat(chat_id)
        
        def reply_text(self, text):
            return text
    
    class MockUpdate:
        def __init__(self, update_id, message_id, text, user_id, first_name, chat_id):
            self.update_id = update_id
            self.message = MockMessage(message_id, text, user_id, first_name, chat_id)
            self.effective_user = self.message.from_user
    
    return MockUpdate(123456, 1, "Test message", 987654, "Test User", 987654)