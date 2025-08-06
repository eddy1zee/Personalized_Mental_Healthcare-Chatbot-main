from textblob import TextBlob
from Simple_Authenticated_Chatbot import analyze_sentiment_and_risk

# Test the basic TextBlob example first
print("=== Basic TextBlob Test ===")
text = "I love learning Python. It's so exciting!"
blob = TextBlob(text)
print(f"Text: {text}")
print(f"Sentiment: {blob.sentiment}")
print()

# Test crisis messages
test_messages = [
    'Hello, how are you today?',
    'I am feeling sad and depressed',
    'I feel hopeless and worthless',
    'I want to kill myself',
    'I want to cut myself',
    'I am going to hurt myself',
    'I feel like cutting'
]

print('=== Crisis Detection Test ===')
for msg in test_messages:
    print(f'Testing: "{msg}"')

    # Show raw TextBlob result
    blob = TextBlob(msg)
    print(f'  TextBlob: polarity={blob.sentiment.polarity:.2f}, subjectivity={blob.sentiment.subjectivity:.2f}')

    # Show our analysis
    sentiment_score, risk_score, crisis_level, sentiment_label = analyze_sentiment_and_risk(msg)
    print(f'  Our Result: Risk={risk_score}/10 ({crisis_level}), Sentiment={sentiment_label} ({sentiment_score:.2f})')
    print()
