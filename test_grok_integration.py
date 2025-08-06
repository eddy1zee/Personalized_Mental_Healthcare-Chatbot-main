#!/usr/bin/env python3
"""
Test script for Groq API integration
This script tests the basic functionality of the Groq API connection
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_groq_api():
    """Test the Groq API connection and basic functionality"""

    print("🧪 Testing Groq API Integration...")
    print("=" * 50)

    # Check environment variables
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key or api_key == "your_groq_api_key_here":
        print("❌ ERROR: GROQ_API_KEY not configured properly")
        print("Please update your .env file with a valid Groq API key")
        print("Get one from: https://console.groq.com/")
        return False

    print(f"🔑 API Key: {'*' * 20}{api_key[-8:] if len(api_key) > 8 else '***'}")

    try:
        # Import and test Groq client
        from groq import Groq

        print("📦 Groq SDK imported successfully")

        # Initialize client
        client = Groq(api_key=api_key)
        print("🔗 Groq client initialized")

        # Simple test message
        print("\n🚀 Sending test request to Groq API...")

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful mental health support assistant. Respond briefly and compassionately."
                },
                {
                    "role": "user",
                    "content": "Hello, can you help me with anxiety?"
                }
            ],
            max_tokens=100,
            temperature=0.7
        )

        bot_response = response.choices[0].message.content

        print("✅ SUCCESS: Groq API is working!")
        print(f"🤖 Groq Response: {bot_response}")
        print(f"⚡ Model used: {response.model}")
        print(f"🔢 Tokens used: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
        print("\n🎉 Your mental health chatbot is ready to use Groq AI!")
        return True

    except ImportError:
        print("❌ ERROR: Groq SDK not installed")
        print("Please install it with: pip install groq")
        return False

    except Exception as e:
        error_msg = str(e)

        if "401" in error_msg or "unauthorized" in error_msg.lower():
            print("❌ ERROR: Authentication failed")
            print("Please check your API key at https://console.groq.com/")

        elif "429" in error_msg or "rate limit" in error_msg.lower():
            print("⚠️  WARNING: Rate limit exceeded")
            print("Please wait a moment and try again")
            print("Note: Groq has generous free tier limits!")

        elif "404" in error_msg or "not found" in error_msg.lower():
            print("❌ ERROR: Model or endpoint not found")
            print("The llama-3.3-70b-versatile model might not be available")

        else:
            print(f"❌ ERROR: {error_msg}")

    return False

def test_knowledge_base():
    """Test if the knowledge base CSV file is accessible"""
    
    print("\n📚 Testing Knowledge Base...")
    print("=" * 30)
    
    csv_paths = [
        "AI_Mental_Health.csv",
        "../AI_Mental_Health.csv",
        "Personalized_Mental_Healthcare-Chatbot-main/AI_Mental_Health.csv"
    ]
    
    for csv_path in csv_paths:
        if os.path.exists(csv_path):
            try:
                import pandas as pd
                df = pd.read_csv(csv_path)
                print(f"✅ Knowledge base found: {csv_path}")
                print(f"📊 Entries: {len(df)} Q&A pairs")
                return True
            except Exception as e:
                print(f"⚠️  Found CSV but couldn't read: {e}")
    
    print("❌ Knowledge base CSV not found")
    print("The chatbot will work with API only")
    return False

def main():
    """Main test function"""

    print("🧠 Mental Health Chatbot - Groq Integration Test")
    print("=" * 60)

    # Test API
    api_success = test_groq_api()

    # Test knowledge base
    kb_success = test_knowledge_base()

    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 20)
    print(f"⚡ Groq API: {'✅ Working' if api_success else '❌ Failed'}")
    print(f"📚 Knowledge Base: {'✅ Available' if kb_success else '⚠️  Not found'}")

    if api_success:
        print("\n🎉 READY TO GO!")
        print("Your chatbot can use Groq's lightning-fast AI for advanced responses")
        print("⚡ Groq offers some of the fastest inference speeds available!")
    elif kb_success:
        print("\n⚠️  PARTIAL FUNCTIONALITY")
        print("Your chatbot can use the knowledge base but not Groq AI")
    else:
        print("\n❌ SETUP REQUIRED")
        print("Please configure your API key and check the knowledge base")

    print("\n🚀 To run your chatbot:")
    print("streamlit run Personalized_Mental_Healthcare-Chatbot.py")

    if api_success:
        print("\n💡 Groq Benefits:")
        print("• Ultra-fast response times (often under 1 second)")
        print("• Generous free tier with high rate limits")
        print("• High-quality Llama models")
        print("• Cost-effective for production use")

if __name__ == "__main__":
    main()
