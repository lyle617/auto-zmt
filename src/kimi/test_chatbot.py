import unittest
from .chatbot import Chatbot

class TestChatbot(unittest.TestCase):
    def setUp(self):
        self.chatbot = Chatbot()

    def test_create_conversation(self):
        response = self.chatbot.create_conversation("Test Conversation")
        self.assertIsInstance(response, dict)
        self.assertIn("id", response)

    def test_get_conversations(self):
        response = self.chatbot.get_conversations(size=5)
        self.assertIsInstance(response, dict)
        self.assertIn("conversations", response)

    def test_get_history(self):
        conversation_id = self.chatbot.create_conversation("Test History")["id"]
        response = self.chatbot.get_history(conversation_id, last=10)
        self.assertIsInstance(response, dict)
        self.assertIn("segments", response)

if __name__ == "__main__":
    unittest.main()