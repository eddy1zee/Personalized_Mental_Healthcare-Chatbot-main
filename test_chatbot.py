"""
Test script for the Mental Health Chatbot
Tests core functionality without requiring API keys
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add project directory to path
sys.path.append('Project')

class TestMentalHealthChatbot(unittest.TestCase):
    """Test cases for the mental health chatbot"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock environment variables
        os.environ['OPENAI_API_KEY'] = 'test-key'
    
    def test_imports(self):
        """Test that all required modules can be imported"""
        try:
            from Project import config
            from Project import models
            from Project import utils
            print("✅ All modules imported successfully")
        except ImportError as e:
            self.fail(f"Import failed: {e}")
    
    def test_config_loading(self):
        """Test configuration loading"""
        try:
            from Project.config import CHAT_MODEL, MAX_TOKENS, TEMPERATURE, SYSTEM_PROMPT
            
            self.assertIsInstance(CHAT_MODEL, str)
            self.assertIsInstance(MAX_TOKENS, int)
            self.assertIsInstance(TEMPERATURE, float)
            self.assertIsInstance(SYSTEM_PROMPT, str)
            
            print("✅ Configuration loaded successfully")
            print(f"   Model: {CHAT_MODEL}")
            print(f"   Max Tokens: {MAX_TOKENS}")
            print(f"   Temperature: {TEMPERATURE}")
            
        except Exception as e:
            self.fail(f"Config loading failed: {e}")
    
    def test_utils_functions(self):
        """Test utility functions"""
        try:
            from Project.utils import preprocess, get_context, decode_response
            
            # Test preprocessing
            test_input = "  Hello   world  \n  "
            processed = preprocess(test_input)
            self.assertEqual(processed, "Hello world")
            
            # Test context detection
            context = get_context("I feel anxious")
            self.assertIn(context, ["MentalHealthChatbot", "CRISIS"])
            
            # Test response decoding
            response = decode_response("Hello")
            self.assertEqual(response, "Hello.")
            
            print("✅ Utility functions working correctly")
            
        except Exception as e:
            self.fail(f"Utils test failed: {e}")
    
    def test_crisis_detection(self):
        """Test crisis keyword detection"""
        try:
            from Project.models import detect_crisis_keywords, get_crisis_response
            
            # Test crisis detection
            crisis_text = "I want to hurt myself"
            keywords = detect_crisis_keywords(crisis_text)
            self.assertTrue(len(keywords) > 0)
            
            # Test crisis response
            response = get_crisis_response()
            self.assertIn("988", response)
            self.assertIn("crisis", response.lower())
            
            print("✅ Crisis detection working correctly")
            print(f"   Detected keywords: {keywords}")
            
        except Exception as e:
            self.fail(f"Crisis detection test failed: {e}")
    
    @patch('Project.models.OpenAI')
    def test_model_initialization(self, mock_openai):
        """Test model initialization with mocked OpenAI"""
        try:
            from Project.models import MentalHealthChatbot
            
            # Mock the OpenAI client
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            # Initialize chatbot
            chatbot = MentalHealthChatbot()
            self.assertIsNotNone(chatbot)
            
            print("✅ Model initialization successful")
            
        except Exception as e:
            self.fail(f"Model initialization failed: {e}")
    
    def test_knowledge_base_loading(self):
        """Test knowledge base loading"""
        try:
            from Project.utils import load_mental_health_data
            
            # Test with non-existent file
            kb = load_mental_health_data("nonexistent.csv")
            self.assertEqual(kb, {})
            
            # Test with actual file if it exists
            if os.path.exists("AI_Mental_Health.csv"):
                kb = load_mental_health_data("AI_Mental_Health.csv")
                self.assertIsInstance(kb, dict)
                print(f"✅ Knowledge base loaded: {len(kb)} entries")
            else:
                print("⚠️ AI_Mental_Health.csv not found, skipping knowledge base test")
            
        except Exception as e:
            self.fail(f"Knowledge base test failed: {e}")
    
    def test_voice_input_module(self):
        """Test voice input module imports"""
        try:
            from Project.voice_input import check_microphone_access, display_voice_requirements
            
            # Test microphone check (will likely fail without actual mic)
            mic_available = check_microphone_access()
            print(f"✅ Voice input module loaded (Microphone available: {mic_available})")
            
        except Exception as e:
            print(f"⚠️ Voice input test failed (expected if SpeechRecognition not installed): {e}")

def run_basic_functionality_test():
    """Run a basic functionality test without API calls"""
    print("\n🧪 Running Basic Functionality Test...")
    
    try:
        # Test environment setup
        print("1. Testing environment setup...")
        os.environ['OPENAI_API_KEY'] = 'test-key-for-testing'
        
        # Test imports
        print("2. Testing imports...")
        sys.path.append('Project')
        from Project.utils import preprocess, extract_keywords
        from Project.models import detect_crisis_keywords
        
        # Test text processing
        print("3. Testing text processing...")
        test_text = "I feel really anxious and overwhelmed lately"
        processed = preprocess(test_text)
        keywords = extract_keywords(processed)
        crisis_keywords = detect_crisis_keywords(processed)
        
        print(f"   Original: {test_text}")
        print(f"   Processed: {processed}")
        print(f"   Keywords: {keywords}")
        print(f"   Crisis keywords: {crisis_keywords}")
        
        # Test configuration
        print("4. Testing configuration...")
        from Project.config import CHAT_MODEL, SYSTEM_PROMPT
        print(f"   Model: {CHAT_MODEL}")
        print(f"   System prompt length: {len(SYSTEM_PROMPT)} characters")
        
        print("\n✅ Basic functionality test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Basic functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Mental Health Chatbot Test Suite")
    print("=" * 50)
    
    # Run basic functionality test first
    basic_test_passed = run_basic_functionality_test()
    
    if basic_test_passed:
        print("\n🧪 Running Unit Tests...")
        unittest.main(verbosity=2, exit=False)
    else:
        print("\n❌ Basic tests failed. Please fix issues before running unit tests.")
    
    print("\n📋 Test Summary:")
    print("- Check that all required packages are installed")
    print("- Verify OpenAI API key is set in .env file")
    print("- Ensure AI_Mental_Health.csv is in the correct location")
    print("- Test the Streamlit app with: streamlit run Personalized_Mental_Healthcare-Chatbot.py")
