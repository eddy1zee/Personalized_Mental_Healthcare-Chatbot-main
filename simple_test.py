"""
Simple test to verify the chatbot components work
"""

import os
import sys

def test_basic_imports():
    """Test basic Python imports"""
    print("Testing basic imports...")
    try:
        import pandas as pd
        import streamlit as st
        from dotenv import load_dotenv
        print("✅ Basic imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_openai_import():
    """Test OpenAI import"""
    print("Testing OpenAI import...")
    try:
        from openai import OpenAI
        print("✅ OpenAI import successful")
        return True
    except ImportError as e:
        print(f"❌ OpenAI import failed: {e}")
        return False

def test_speech_recognition():
    """Test speech recognition import"""
    print("Testing speech recognition...")
    try:
        import speech_recognition as sr
        print("✅ Speech recognition import successful")
        return True
    except ImportError as e:
        print(f"❌ Speech recognition import failed: {e}")
        return False

def test_csv_loading():
    """Test CSV file loading"""
    print("Testing CSV file loading...")
    try:
        import pandas as pd
        
        # Try to load the mental health dataset
        csv_path = "AI_Mental_Health.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            print(f"✅ CSV loaded successfully: {len(df)} rows")
            print(f"   Columns: {list(df.columns)}")
            return True
        else:
            print(f"⚠️ CSV file not found at {csv_path}")
            return False
    except Exception as e:
        print(f"❌ CSV loading failed: {e}")
        return False

def test_env_file():
    """Test environment file"""
    print("Testing environment configuration...")
    
    # Check if .env.example exists
    if os.path.exists(".env.example"):
        print("✅ .env.example file found")
    else:
        print("⚠️ .env.example file not found")
    
    # Check if .env exists
    if os.path.exists(".env"):
        print("✅ .env file found")
        
        # Load and check for API key
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key_here":
            print("✅ OpenAI API key configured")
            return True
        else:
            print("⚠️ OpenAI API key not configured in .env")
            return False
    else:
        print("⚠️ .env file not found - you'll need to create one")
        return False

def test_project_structure():
    """Test project structure"""
    print("Testing project structure...")
    
    required_files = [
        "Personalized_Mental_Healthcare-Chatbot.py",
        "requirements.txt",
        "AI_Mental_Health.csv",
        "Project/app.py",
        "Project/models.py",
        "Project/utils.py",
        "Project/config.py",
        "Project/voice_input.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if not missing_files:
        print("✅ All required files present")
        return True
    else:
        print(f"❌ Missing files: {missing_files}")
        return False

def main():
    """Run all tests"""
    print("🧪 Simple Chatbot Test")
    print("=" * 40)
    
    tests = [
        test_basic_imports,
        test_openai_import,
        test_speech_recognition,
        test_project_structure,
        test_csv_loading,
        test_env_file
    ]
    
    results = []
    for test in tests:
        print()
        result = test()
        results.append(result)
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The chatbot should work correctly.")
        print("\n🚀 Next steps:")
        print("1. Create a .env file with your OpenAI API key")
        print("2. Run: streamlit run Personalized_Mental_Healthcare-Chatbot.py")
    else:
        print("⚠️ Some tests failed. Please address the issues above.")
        
        if not os.path.exists(".env"):
            print("\n📝 To create .env file:")
            print("1. Copy .env.example to .env")
            print("2. Add your OpenAI API key")
            print("3. Get API key from: https://platform.openai.com/api-keys")

if __name__ == "__main__":
    main()
