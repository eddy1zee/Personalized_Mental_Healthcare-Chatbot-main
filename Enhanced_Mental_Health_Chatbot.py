import os
import pandas as pd
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import logging
import time
import smtplib
import email.mime.text
import email.mime.multipart
from textblob import TextBlob
import re

# Load environment variables
load_dotenv()

# Initialize Groq client
try:
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    groq_client = None
    logging.warning(f"Groq client initialization failed: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Crisis keywords for detection
CRISIS_KEYWORDS = [
    'suicide', 'kill myself', 'end my life', 'want to die', 'better off dead',
    'no point living', 'can\'t go on', 'end it all', 'hurt myself', 'self harm',
    'cutting', 'overdose', 'jump off', 'hang myself', 'worthless', 'hopeless',
    'can\'t take it anymore', 'nobody cares', 'everyone would be better without me'
]

def analyze_sentiment_and_risk(text):
    """
    Analyze sentiment and calculate crisis risk score
    Returns: (sentiment_score, risk_score, crisis_level, sentiment_label)
    """
    try:
        # TextBlob sentiment analysis
        blob = TextBlob(text.lower())
        sentiment_score = blob.sentiment.polarity  # -1 to 1
        
        # Initialize risk score
        risk_score = 0
        
        # Check for crisis keywords
        crisis_count = sum(1 for keyword in CRISIS_KEYWORDS if keyword in text.lower())
        
        # Calculate risk based on sentiment and crisis keywords
        if sentiment_score < -0.5:  # Very negative sentiment
            risk_score += 3
        elif sentiment_score < -0.2:  # Negative sentiment
            risk_score += 2
        elif sentiment_score < 0:  # Slightly negative
            risk_score += 1
            
        # Add risk for crisis keywords
        risk_score += crisis_count * 2
        
        # Additional risk factors
        if any(word in text.lower() for word in ['depressed', 'anxiety', 'panic', 'scared']):
            risk_score += 1
            
        # Cap risk score at 10
        risk_score = min(risk_score, 10)
        
        # Determine crisis level
        if risk_score >= 8:
            crisis_level = "SEVERE"
        elif risk_score >= 6:
            crisis_level = "HIGH"
        elif risk_score >= 4:
            crisis_level = "MODERATE"
        else:
            crisis_level = "LOW"
            
        # Sentiment label
        if sentiment_score > 0.1:
            sentiment_label = "POSITIVE"
        elif sentiment_score < -0.1:
            sentiment_label = "NEGATIVE"
        else:
            sentiment_label = "NEUTRAL"
            
        return sentiment_score, risk_score, crisis_level, sentiment_label
        
    except Exception as e:
        logging.error(f"Sentiment analysis error: {e}")
        return 0, 0, "LOW", "NEUTRAL"

def send_crisis_email(user_message, risk_score, contact_info=None):
    """
    Send crisis alert email to counselor
    """
    try:
        email_user = os.getenv("EMAIL_USER")
        email_password = os.getenv("EMAIL_PASSWORD")
        counselor_email = os.getenv("COUNSELOR_EMAIL")
        
        if not all([email_user, email_password, counselor_email]):
            logging.warning("Email configuration incomplete")
            return False
            
        # Create message
        msg = email.mime.multipart.MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = counselor_email
        msg['Subject'] = f"🚨 CRISIS ALERT - Risk Score: {risk_score}/10"

        body = f"""
        CRISIS ALERT - Mental Health Chatbot

        Risk Score: {risk_score}/10
        Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}

        User Message:
        "{user_message}"

        Contact Information:
        {contact_info if contact_info else 'Not provided'}

        Please follow up immediately if this is a genuine crisis.

        - Mental Health Chatbot System
        """

        msg.attach(email.mime.text.MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_password)
        text = msg.as_string()
        server.sendmail(email_user, counselor_email, text)
        server.quit()
        
        return True
        
    except Exception as e:
        logging.error(f"Email sending error: {e}")
        return False

def display_crisis_intervention(risk_score, user_message):
    """
    Display crisis intervention interface
    """
    st.error("🚨 **CRISIS ALERT DETECTED**")
    st.warning(f"**Risk Level: {risk_score}/10**")
    
    # Emergency resources
    st.markdown("### 🆘 **IMMEDIATE HELP AVAILABLE:**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🚨 Emergency Services:**
        - **Call 911** (Life-threatening emergency)
        - **988** (Suicide & Crisis Lifeline)
        - **Text HOME to 741741** (Crisis Text Line)
        """)
        
    with col2:
        st.markdown("""
        **💬 Online Support:**
        - **suicidepreventionlifeline.org**
        - **crisistextline.org**
        - **nami.org** (Mental Health Support)
        """)
    
    # Contact form
    st.markdown("### 📞 **Professional Help Contact**")
    with st.form("crisis_contact_form"):
        st.write("A mental health professional will be notified. Please provide contact information:")
        
        name = st.text_input("Your Name (optional)")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email Address")
        additional_info = st.text_area("Additional Information (optional)")
        
        consent = st.checkbox("I consent to sharing this information with a mental health professional")
        
        if st.form_submit_button("🚨 Send Crisis Alert", type="primary"):
            if consent and (phone or email):
                contact_info = f"Name: {name}\nPhone: {phone}\nEmail: {email}\nAdditional: {additional_info}"
                
                if send_crisis_email(user_message, risk_score, contact_info):
                    st.success("✅ Crisis alert sent successfully! Help is on the way.")
                    st.info("Please stay safe and consider calling emergency services if you're in immediate danger.")
                else:
                    st.error("❌ Unable to send alert. Please call emergency services directly.")
            else:
                st.warning("Please provide contact information and consent to proceed.")

# Groq API client function
def call_groq_api(messages, model="llama-3.3-70b-versatile", max_tokens=800, temperature=0.7):
    """
    Call Groq API for chat completions using the official SDK
    """
    try:
        if not groq_client:
            logging.error("Groq client not initialized")
            return None

        response = groq_client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        return response.choices[0].message.content

    except Exception as e:
        logging.error(f"Groq API error: {e}")
        return None

# Load mental health dataset
try:
    csv_paths = [
        "AI_Mental_Health.csv",
        "../AI_Mental_Health.csv",
        "Personalized_Mental_Healthcare-Chatbot-main/AI_Mental_Health.csv"
    ]

    mentalhealth = None
    csv_path_used = None

    for csv_path in csv_paths:
        try:
            mentalhealth = pd.read_csv(csv_path)
            csv_path_used = csv_path
            break
        except FileNotFoundError:
            continue

    if mentalhealth is not None:
        knowledge_base = {}
        for i in range(len(mentalhealth)):
            question = str(mentalhealth.iloc[i]["Questions"]).lower()
            answer = str(mentalhealth.iloc[i]["Answers"])
            if question and answer and question != 'nan' and answer != 'nan':
                knowledge_base[question] = answer

        st.success(f"✅ Mental health dataset loaded successfully! ({len(knowledge_base)} Q&A pairs from {csv_path_used})")
    else:
        raise FileNotFoundError("CSV file not found in any expected location")

except FileNotFoundError:
    st.error("❌ Mental health dataset not found. Please ensure AI_Mental_Health.csv is in the correct location.")
    knowledge_base = {}
except Exception as e:
    st.error(f"❌ Error loading mental health dataset: {e}")
    knowledge_base = {}

# Enhanced response generation with sentiment analysis
def generate_enhanced_response(input_text):
    """
    Generate response with sentiment analysis and crisis detection
    """
    try:
        # Analyze sentiment and risk
        sentiment_score, risk_score, crisis_level, sentiment_label = analyze_sentiment_and_risk(input_text)

        # Display sentiment dashboard
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Risk Score", f"{risk_score}/10")
        with col2:
            st.metric("Crisis Level", crisis_level)
        with col3:
            st.metric("Sentiment", sentiment_label)
        with col4:
            sentiment_color = "🟢" if sentiment_score > 0 else "🔴" if sentiment_score < -0.2 else "🟡"
            st.metric("Mood", f"{sentiment_color} {sentiment_score:.2f}")

        # Crisis intervention if high risk
        if risk_score >= 6:
            display_crisis_intervention(risk_score, input_text)
            return  # Don't generate normal response for crisis situations

        # Search knowledge base
        relevant_context = ""
        user_input_lower = input_text.lower()
        direct_matches = []

        for question, answer in knowledge_base.items():
            if any(word in question for word in user_input_lower.split()):
                direct_matches.append((question, answer))
                relevant_context += f"Q: {question}\nA: {answer}\n\n"

        # Enhanced system prompt based on risk level
        if risk_score >= 4:
            system_prompt = f"""You are WellBot, a compassionate mental health chatbot. The user is showing signs of distress (Risk: {risk_score}/10, Sentiment: {sentiment_label}). Be extra empathetic, validate their feelings, and gently encourage professional help. Provide specific coping strategies and resources. Never diagnose.

            Context: {relevant_context[:1000] if relevant_context else 'Mental health support for someone in distress'}"""
        else:
            system_prompt = f"""You are WellBot, a supportive mental health chatbot. The user seems to be in a stable state (Risk: {risk_score}/10, Sentiment: {sentiment_label}). Provide helpful, encouraging responses while maintaining professional boundaries. Never diagnose.

            Context: {relevant_context[:1000] if relevant_context else 'General mental health support'}"""

        # Generate response
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_text}
        ]

        bot_response = call_groq_api(
            messages=messages,
            model="llama-3.3-70b-versatile",
            max_tokens=800,
            temperature=0.7
        )

        if bot_response:
            st.success("✅")
            st.write("**🤖 WellBot :** " + bot_response)

            # Additional resources for moderate risk
            if risk_score >= 3:
                st.info("💙 **Additional Resources:** If you're struggling, consider reaching out to a mental health professional or calling 988 for support.")
        else:
            st.error("❌ Unable to generate response. Please try again.")

    except Exception as e:
        logging.error(f"Error in enhanced response generation: {e}")
        st.error(f"🚨 Error: {e}")

def get_enhanced_bot_response(input_text):
    """
    Get bot response with sentiment analysis (for chat history)
    """
    try:
        sentiment_score, risk_score, crisis_level, sentiment_label = analyze_sentiment_and_risk(input_text)

        # For crisis situations, return crisis message
        if risk_score >= 6:
            return f"🚨 CRISIS DETECTED (Risk: {risk_score}/10) - Please seek immediate help. Call 988 or emergency services."

        # Search knowledge base
        relevant_context = ""
        user_input_lower = input_text.lower()

        for question, answer in knowledge_base.items():
            if any(word in question for word in user_input_lower.split()):
                relevant_context += f"Q: {question}\nA: {answer}\n\n"
                break

        # Enhanced system prompt
        system_prompt = f"""You are WellBot, a mental health chatbot. User sentiment: {sentiment_label} (Risk: {risk_score}/10). Respond appropriately to their emotional state. Be supportive and professional.

        Context: {relevant_context[:800] if relevant_context else 'Mental health support'}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_text}
        ]

        bot_response = call_groq_api(
            messages=messages,
            model="llama-3.3-70b-versatile",
            max_tokens=600,
            temperature=0.7
        )

        return bot_response if bot_response else "I'm here to support you. Please try again or contact a professional if you need immediate help."

    except Exception as e:
        logging.error(f"Error in get_enhanced_bot_response: {e}")
        return "I'm experiencing technical difficulties. If you're in crisis, please call 988 or emergency services."

# Main application
def main():
    st.set_page_config(
        page_title="Enhanced Mental Health Chatbot - AI Powered",
        page_icon="🧠",
        layout="wide"
    )

    st.title("🧠 Enhanced Mental Health Chatbot")
    st.markdown("🎯 **AI-Powered with Sentiment Analysis & Crisis Detection**")
    st.markdown("---")

    # Sidebar with enhanced information
    with st.sidebar:
        st.header("ℹ️ About Enhanced Features")
        st.write("✅ **Real-time sentiment analysis**")
        st.write("✅ **Crisis risk assessment**")
        st.write("✅ **Automatic crisis intervention**")
        st.write("✅ **Professional alert system**")

        st.markdown("---")
        st.header("🚨 Crisis Resources")
        st.write("**If you're in crisis, please reach out immediately:**")
        st.write("- **National Suicide Prevention Lifeline:** 988")
        st.write("- **Crisis Text Line:** Text HOME to 741741")
        st.write("- **Emergency Services:** 911")

        st.markdown("---")
        st.header("📊 Dashboard Legend")
        st.write("**Risk Levels:**")
        st.write("- 🟢 **0-3:** Low Risk")
        st.write("- 🟡 **4-5:** Moderate Risk")
        st.write("- 🟠 **6-7:** High Risk")
        st.write("- 🔴 **8-10:** Severe Risk")

    # Main interface
    st.subheader("💬 Chat Interface")

    # Create columns for input and response
    input_col, response_col = st.columns([1, 1])

    with input_col:
        st.markdown("### 💭 Your Message")

        with st.form(key="enhanced_chat_form", clear_on_submit=True):
            input_text = st.text_area(
                "Share what's on your mind:",
                placeholder="I'm here to listen and provide support...",
                height=150,
                key="enhanced_message_input"
            )

            col1, col2 = st.columns([1, 1])
            with col1:
                send_clicked = st.form_submit_button("Send 📤", type="primary")
            with col2:
                pass

        # Clear chat button
        if st.button("Clear Chat 🗑️"):
            if 'enhanced_chat_history' in st.session_state:
                st.session_state.enhanced_chat_history = []
            st.rerun()

        # Handle form submission
        if send_clicked and input_text.strip():
            with st.spinner("🤖 Analyzing and responding..."):
                # Initialize chat history
                if 'enhanced_chat_history' not in st.session_state:
                    st.session_state.enhanced_chat_history = []

                # Get response
                response = get_enhanced_bot_response(input_text.strip())

                # Add to chat history
                st.session_state.enhanced_chat_history.append({
                    'user': input_text.strip(),
                    'bot': response,
                    'timestamp': time.time()
                })

                st.success("✅ Message processed!")

        elif send_clicked:
            st.warning("Please enter a message first.")

    with response_col:
        st.markdown("### 🤖 WellBot Enhanced Responses")

        # Display current conversation with analysis
        if send_clicked and input_text.strip():
            st.markdown("#### 📊 Current Analysis")
            generate_enhanced_response(input_text.strip())

        # Chat history
        if 'enhanced_chat_history' in st.session_state and st.session_state.enhanced_chat_history:
            st.markdown("#### 💬 Recent Conversations")
            for i, chat in enumerate(reversed(st.session_state.enhanced_chat_history[-3:])):
                with st.expander(f"Conversation {len(st.session_state.enhanced_chat_history) - i}", expanded=(i == 0)):
                    st.markdown("**You:**")
                    st.info(chat['user'])
                    st.markdown("**🤖 WellBot:**")
                    st.success(chat['bot'])
                    st.caption(f"⏰ {time.strftime('%H:%M:%S', time.localtime(chat['timestamp']))}")
        else:
            st.info("💡 Your enhanced conversations will appear here...")
            st.markdown("**New Features:**")
            st.write("• Real-time sentiment analysis")
            st.write("• Crisis risk assessment")
            st.write("• Automatic professional alerts")
            st.write("• Enhanced emotional support")

    # Quick test buttons
    st.markdown("---")
    st.subheader("🧪 Test Scenarios")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("😊 Positive Test"):
            test_input = "I'm feeling great today and excited about my future!"
            generate_enhanced_response(test_input)

    with col2:
        if st.button("😔 Moderate Risk Test"):
            test_input = "I'm really struggling with depression and don't know what to do"
            generate_enhanced_response(test_input)

    with col3:
        if st.button("🚨 Crisis Test"):
            test_input = "I can't take this anymore, I want to end my life"
            generate_enhanced_response(test_input)

if __name__ == '__main__':
    main()
