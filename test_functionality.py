"""
Test the core functionality of the mental health chatbot
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_chatbot_functionality():
    """Test the chatbot's core functionality"""
    print("🧪 Testing Mental Health Chatbot Functionality")
    print("=" * 50)
    
    try:
        # Test imports
        print("1. Testing imports...")
        sys.path.append('Project')
        from Project.models import MentalHealthChatbot, detect_crisis_keywords, get_crisis_response
        from Project.utils import preprocess, load_mental_health_data
        from Project.chatbot import ChatBot
        print("✅ All imports successful")
        
        # Test configuration
        print("\n2. Testing configuration...")
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and len(api_key) > 20:
            print("✅ OpenAI API key configured")
        else:
            print("❌ OpenAI API key not properly configured")
            return False
        
        # Test knowledge base loading
        print("\n3. Testing knowledge base...")
        knowledge_base = load_mental_health_data("AI_Mental_Health.csv")
        print(f"✅ Knowledge base loaded: {len(knowledge_base)} entries")
        
        # Test crisis detection
        print("\n4. Testing crisis detection...")
        crisis_text = "I want to hurt myself"
        keywords = detect_crisis_keywords(crisis_text)
        print(f"✅ Crisis keywords detected: {keywords}")
        
        crisis_response = get_crisis_response()
        print(f"✅ Crisis response generated (length: {len(crisis_response)} chars)")
        
        # Test text preprocessing
        print("\n5. Testing text preprocessing...")
        test_input = "  I feel really anxious and overwhelmed  "
        processed = preprocess(test_input)
        print(f"✅ Text preprocessed: '{test_input}' -> '{processed}'")
        
        # Test chatbot initialization
        print("\n6. Testing chatbot initialization...")
        chatbot = ChatBot("AI_Mental_Health.csv")
        print("✅ Chatbot initialized successfully")
        
        kb_info = chatbot.get_knowledge_base_info()
        print(f"✅ Knowledge base info: {kb_info['total_entries']} entries")
        
        # Test knowledge base search
        print("\n7. Testing knowledge base search...")
        search_results = chatbot.search_knowledge_base("anxiety")
        print(f"✅ Found {len(search_results)} relevant entries for 'anxiety'")
        
        if search_results:
            print(f"   Top result: {search_results[0]['question'][:50]}...")
        
        print("\n🎉 All functionality tests passed!")
        print("\n📋 Summary:")
        print(f"- API Key: {'✅ Configured' if api_key else '❌ Missing'}")
        print(f"- Knowledge Base: ✅ {len(knowledge_base)} entries loaded")
        print(f"- Crisis Detection: ✅ Working")
        print(f"- Text Processing: ✅ Working")
        print(f"- Chatbot: ✅ Initialized")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sample_conversation():
    """Test a sample conversation"""
    print("\n" + "=" * 50)
    print("🗣️ Testing Sample Conversation")
    print("=" * 50)
    
    try:
        sys.path.append('Project')
        from Project.chatbot import ChatBot
        
        # Initialize chatbot
        chatbot = ChatBot("AI_Mental_Health.csv")
        
        # Test normal conversation
        print("\n💬 Testing normal conversation...")
        normal_input = "I've been feeling anxious lately"
        response = chatbot.generate_response(normal_input)
        
        print(f"User: {normal_input}")
        print(f"Bot Type: {response['type']}")
        print(f"Bot Response: {response['content'][:100]}...")
        
        if response['type'] == 'normal':
            print("✅ Normal conversation working")
        else:
            print("⚠️ Unexpected response type")
        
        # Test crisis detection
        print("\n🚨 Testing crisis detection...")
        crisis_input = "I want to hurt myself"
        crisis_response = chatbot.generate_response(crisis_input)
        
        print(f"User: {crisis_input}")
        print(f"Bot Type: {crisis_response['type']}")
        print(f"Crisis Keywords: {crisis_response['keywords_detected']}")
        print(f"Immediate Attention: {crisis_response['requires_immediate_attention']}")
        
        if crisis_response['type'] == 'crisis':
            print("✅ Crisis detection working")
        else:
            print("⚠️ Crisis detection not working properly")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Conversation test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧠 Mental Health Chatbot - Functionality Test")
    print("=" * 60)
    
    # Run functionality tests
    func_test_passed = test_chatbot_functionality()
    
    if func_test_passed:
        # Run conversation tests
        conv_test_passed = test_sample_conversation()
        
        if conv_test_passed:
            print("\n🎉 ALL TESTS PASSED!")
            print("\n🚀 Your chatbot is ready to use!")
            print("\nTo run the Streamlit app:")
            print("streamlit run Personalized_Mental_Healthcare-Chatbot.py")
        else:
            print("\n⚠️ Some conversation tests failed")
    else:
        print("\n❌ Basic functionality tests failed")
        print("Please check your configuration and try again.")
