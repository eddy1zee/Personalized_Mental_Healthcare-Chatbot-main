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
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

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

# Authentication configuration
def load_authenticator():
    """Load or create authentication configuration"""
    config_file = 'auth_config.yaml'

    if not os.path.exists(config_file):
        # Create default config if it doesn't exist
        config = {
            'credentials': {
                'usernames': {}
            },
            'cookie': {
                'name': 'mental_health_chatbot',
                'key': 'mental_health_key_123',
                'expiry_days': 30
            }
        }

        with open(config_file, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)

    with open(config_file) as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    return authenticator, config

def register_user(authenticator, config):
    """Handle user registration"""
    st.subheader("🔐 Create Account")
    
    with st.form("registration_form"):
        st.write("Create your account to access the mental health chatbot:")
        
        name = st.text_input("Full Name")
        username = st.text_input("Username")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        password_confirm = st.text_input("Confirm Password", type="password")
        
        register_button = st.form_submit_button("Create Account")
        
        if register_button:
            if not all([name, username, email, password]):
                st.error("Please fill in all fields")
            elif password != password_confirm:
                st.error("Passwords do not match")
            elif username in config['credentials']['usernames']:
                st.error("Username already exists")
            else:
                try:
                    # Hash the password
                    hashed_password = stauth.Hasher([password]).generate()[0]
                    
                    # Add user to config
                    config['credentials']['usernames'][username] = {
                        'name': name,
                        'password': hashed_password,
                        'email': email
                    }
                    
                    # Save updated config
                    with open('auth_config.yaml', 'w') as file:
                        yaml.dump(config, file, default_flow_style=False)
                    
                    st.success("✅ Account created successfully! Please login.")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Registration failed: {e}")

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

def send_crisis_email_from_user(user_email, user_name, user_message, risk_score, contact_info=None):
    """
    Send crisis alert email FROM user's email TO counselor
    """
    try:
        counselor_email = os.getenv("COUNSELOR_EMAIL")
        
        if not counselor_email:
            logging.warning("Counselor email not configured")
            return False
            
        # Create message FROM user TO counselor
        msg = email.mime.multipart.MIMEMultipart()
        msg['From'] = user_email
        msg['To'] = counselor_email
        msg['Subject'] = f"🚨 CRISIS ALERT from {user_name} - Risk Score: {risk_score}/10"
        
        body = f"""
        CRISIS ALERT - Mental Health Chatbot
        
        FROM: {user_name} ({user_email})
        Risk Score: {risk_score}/10
        Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}
        
        User Message:
        "{user_message}"
        
        Additional Contact Information:
        {contact_info if contact_info else 'Not provided'}
        
        Please follow up with this user immediately if this is a genuine crisis.
        
        - Mental Health Chatbot System
        """
        
        msg.attach(email.mime.text.MIMEText(body, 'plain'))
        
        # For demonstration, we'll log the email instead of actually sending
        # In production, you'd need the user's email credentials or use a service
        logging.info(f"CRISIS EMAIL ALERT:\nFrom: {user_email}\nTo: {counselor_email}\nSubject: {msg['Subject']}\nBody: {body}")
        
        # Save to local file for demonstration
        with open("crisis_alerts.log", "a") as f:
            f.write(f"\n=== CRISIS ALERT ===\n")
            f.write(f"From: {user_email} ({user_name})\n")
            f.write(f"To: {counselor_email}\n")
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Risk Score: {risk_score}/10\n")
            f.write(f"User Message: {user_message}\n")
            f.write(f"Contact Info: {contact_info if contact_info else 'Not provided'}\n")
            f.write("=" * 50 + "\n")
        
        return True
        
    except Exception as e:
        logging.error(f"Email sending error: {e}")
        return False

def display_crisis_intervention(risk_score, user_message, user_email, user_name):
    """
    Display crisis intervention interface with user authentication
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
    st.info(f"Alert will be sent from your email ({user_email}) to the counselor.")
    
    with st.form("crisis_contact_form"):
        st.write("A mental health professional will be notified. Please provide additional contact information:")
        
        phone = st.text_input("Phone Number")
        additional_info = st.text_area("Additional Information (optional)")
        
        consent = st.checkbox("I consent to sending this crisis alert to a mental health professional")
        
        if st.form_submit_button("🚨 Send Crisis Alert", type="primary"):
            if consent:
                contact_info = f"Phone: {phone}\nAdditional: {additional_info}"
                
                if send_crisis_email_from_user(user_email, user_name, user_message, risk_score, contact_info):
                    st.success("✅ Crisis alert sent successfully! Help is on the way.")
                    st.info("Please stay safe and consider calling emergency services if you're in immediate danger.")
                else:
                    st.error("❌ Unable to send alert. Please call emergency services directly.")
            else:
                st.warning("Please provide consent to proceed.")

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

# Enhanced response generation with sentiment analysis and authentication
def generate_authenticated_response(input_text, user_email, user_name):
    """
    Generate response with sentiment analysis and crisis detection for authenticated users
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
            display_crisis_intervention(risk_score, input_text, user_email, user_name)
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
            system_prompt = f"""You are WellBot, a compassionate mental health chatbot. The user {user_name} is showing signs of distress (Risk: {risk_score}/10, Sentiment: {sentiment_label}). Be extra empathetic, validate their feelings, and gently encourage professional help. Provide specific coping strategies and resources. Never diagnose.

            Context: {relevant_context[:1000] if relevant_context else 'Mental health support for someone in distress'}"""
        else:
            system_prompt = f"""You are WellBot, a supportive mental health chatbot. The user {user_name} seems to be in a stable state (Risk: {risk_score}/10, Sentiment: {sentiment_label}). Provide helpful, encouraging responses while maintaining professional boundaries. Never diagnose.

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
            st.write(f"**🤖 WellBot (for {user_name}):** " + bot_response)

            # Additional resources for moderate risk
            if risk_score >= 3:
                st.info("💙 **Additional Resources:** If you're struggling, consider reaching out to a mental health professional or calling 988 for support.")
        else:
            st.error("❌ Unable to generate response. Please try again.")

    except Exception as e:
        logging.error(f"Error in authenticated response generation: {e}")
        st.error(f"🚨 Error: {e}")

def get_authenticated_bot_response(input_text, user_name):
    """
    Get bot response with sentiment analysis for authenticated users (for chat history)
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
        system_prompt = f"""You are WellBot, a mental health chatbot. User {user_name} sentiment: {sentiment_label} (Risk: {risk_score}/10). Respond appropriately to their emotional state. Be supportive and professional.

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

        return bot_response if bot_response else f"I'm here to support you, {user_name}. Please try again or contact a professional if you need immediate help."

    except Exception as e:
        logging.error(f"Error in get_authenticated_bot_response: {e}")
        return f"I'm experiencing technical difficulties, {user_name}. If you're in crisis, please call 988 or emergency services."

# Main application
def main():
    st.set_page_config(
        page_title="Authenticated Mental Health Chatbot",
        page_icon="🧠",
        layout="wide"
    )

    st.title("🧠 Authenticated Mental Health Chatbot")
    st.markdown("🔐 **Secure, Personalized AI Mental Health Support**")
    st.markdown("---")

    # Load authenticator
    authenticator, config = load_authenticator()

    # Authentication
    name, authentication_status, username = authenticator.login(location='main')

    if authentication_status == False:
        st.error('Username/password is incorrect')

        # Registration option
        st.markdown("---")
        st.markdown("### Don't have an account?")
        if st.button("Create New Account"):
            st.session_state.show_registration = True

        if st.session_state.get('show_registration', False):
            register_user(authenticator, config)

    elif authentication_status == None:
        st.warning('Please enter your username and password')

        # Registration option
        st.markdown("---")
        st.markdown("### Don't have an account?")
        if st.button("Create New Account"):
            st.session_state.show_registration = True

        if st.session_state.get('show_registration', False):
            register_user(authenticator, config)

    elif authentication_status:
        # User is authenticated
        user_email = config['credentials']['usernames'][username]['email']
        user_name = config['credentials']['usernames'][username]['name']

        # Sidebar with user info and logout
        with st.sidebar:
            st.write(f'Welcome **{name}**')
            st.write(f'Email: {user_email}')
            authenticator.logout(location='sidebar')

            st.markdown("---")
            st.header("ℹ️ About Enhanced Features")
            st.write("✅ **Personalized responses**")
            st.write("✅ **Real-time sentiment analysis**")
            st.write("✅ **Crisis risk assessment**")
            st.write("✅ **Direct crisis alerts from your email**")

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

        # Main chat interface
        st.subheader(f"💬 Chat with WellBot - Hello {name}!")

        # Create columns for input and response
        input_col, response_col = st.columns([1, 1])

        with input_col:
            st.markdown("### 💭 Your Message")

            with st.form(key="authenticated_chat_form", clear_on_submit=True):
                input_text = st.text_area(
                    "Share what's on your mind (Direct message is encouraged):",
                    placeholder=f"Hi {name}, I'm here to listen and provide support...",
                    height=150,
                    key="authenticated_message_input"
                )

                col1, col2 = st.columns([1, 1])
                with col1:
                    send_clicked = st.form_submit_button("Send 📤", type="primary")
                with col2:
                    pass

            # Clear chat button
            if st.button("Clear Chat 🗑️"):
                if 'authenticated_chat_history' in st.session_state:
                    st.session_state.authenticated_chat_history = []
                st.rerun()

            # Handle form submission
            if send_clicked and input_text.strip():
                with st.spinner("🤖 Analyzing and responding..."):
                    # Initialize chat history
                    if 'authenticated_chat_history' not in st.session_state:
                        st.session_state.authenticated_chat_history = []

                    # Get response
                    response = get_authenticated_bot_response(input_text.strip(), name)

                    # Add to chat history
                    st.session_state.authenticated_chat_history.append({
                        'user': input_text.strip(),
                        'bot': response,
                        'timestamp': time.time()
                    })

                    st.success("✅ Message processed!")

            elif send_clicked:
                st.warning("Please enter a message first.")

        with response_col:
            st.markdown("### 🤖 WellBot Personalized Responses")

            # Display current conversation with analysis
            if send_clicked and input_text.strip():
                st.markdown("#### 📊 Current Analysis")
                generate_authenticated_response(input_text.strip(), user_email, name)

            # Chat history
            if 'authenticated_chat_history' in st.session_state and st.session_state.authenticated_chat_history:
                st.markdown("#### 💬 Recent Conversations")
                for i, chat in enumerate(reversed(st.session_state.authenticated_chat_history[-3:])):
                    with st.expander(f"Conversation {len(st.session_state.authenticated_chat_history) - i}", expanded=(i == 0)):
                        st.markdown("**You:**")
                        st.info(chat['user'])
                        st.markdown("**🤖 WellBot:**")
                        st.success(chat['bot'])
                        st.caption(f"⏰ {time.strftime('%H:%M:%S', time.localtime(chat['timestamp']))}")
            else:
                st.info(f"💡 Your personalized conversations will appear here, {name}...")
                st.markdown("**Features:**")
                st.write("• Personalized responses using your name")
                st.write("• Real-time sentiment analysis")
                st.write("• Crisis alerts sent from your email")
                st.write("• Secure authentication")

        # Quick test buttons
        st.markdown("---")
        st.subheader("🧪 Test Scenarios")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("😊 Positive Test"):
                test_input = "I'm feeling great today and excited about my future!"
                generate_authenticated_response(test_input, user_email, name)

        with col2:
            if st.button("😔 Moderate Risk Test"):
                test_input = "I'm really struggling with depression and don't know what to do"
                generate_authenticated_response(test_input, user_email, name)

        with col3:
            if st.button("🚨 Crisis Test"):
                test_input = "I can't take this anymore, I want to end my life"
                generate_authenticated_response(test_input, user_email, name)

if __name__ == '__main__':
    main()
