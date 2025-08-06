"""
Test CSV loading functionality
"""

import pandas as pd
import os

def test_csv_loading():
    """Test if the CSV file can be loaded from the correct location"""
    print("🧪 Testing CSV Loading")
    print("=" * 30)
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}")
    
    # Try different possible locations for the CSV file
    csv_paths = [
        "AI_Mental_Health.csv",  # Same directory
        "../AI_Mental_Health.csv",  # Parent directory
        "Personalized_Mental_Healthcare-Chatbot-main/AI_Mental_Health.csv"  # Full path
    ]
    
    print("\nTesting CSV file locations:")
    for csv_path in csv_paths:
        exists = os.path.exists(csv_path)
        print(f"  {csv_path}: {'✅ Found' if exists else '❌ Not found'}")
        
        if exists:
            try:
                df = pd.read_csv(csv_path)
                print(f"    Successfully loaded: {len(df)} rows, columns: {list(df.columns)}")
                
                # Test knowledge base creation
                knowledge_base = {}
                for i in range(len(df)):
                    question = str(df.iloc[i]["Questions"]).lower()
                    answer = str(df.iloc[i]["Answers"])
                    if question and answer and question != 'nan' and answer != 'nan':
                        knowledge_base[question] = answer
                
                print(f"    Knowledge base created: {len(knowledge_base)} Q&A pairs")
                
                # Show a sample
                if knowledge_base:
                    sample_q = list(knowledge_base.keys())[0]
                    sample_a = knowledge_base[sample_q]
                    print(f"    Sample Q: {sample_q[:50]}...")
                    print(f"    Sample A: {sample_a[:50]}...")
                
                return True, csv_path, knowledge_base
                
            except Exception as e:
                print(f"    ❌ Error loading CSV: {e}")
    
    return False, None, {}

if __name__ == "__main__":
    success, path_used, kb = test_csv_loading()
    
    if success:
        print(f"\n🎉 SUCCESS! CSV loaded from: {path_used}")
        print(f"Knowledge base contains {len(kb)} entries")
        print("\nThe Streamlit app should now work correctly!")
    else:
        print("\n❌ FAILED! Could not load CSV file")
        print("Please check that AI_Mental_Health.csv is in the correct location")
