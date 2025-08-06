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
import hashlib

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
    'cutting', 'cut myself', 'want to cut', 'going to cut', 'overdose', 'jump off',
    'hang myself', 'worthless', 'hopeless', 'can\'t take it anymore', 'can\'t take this anymore',
    'nobody cares', 'everyone would be better without me', 'want to kill myself',
    'going to kill myself', 'self-harm', 'self injury', 'harm myself', 'injure myself', 'bleeding'
]

# Simple user database (in production, use a proper database)
USER_DB_FILE = "users.txt"

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from file"""
    users = {}
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) == 5:  # Updated to handle phone number
                        username, email, name, phone, password_hash = parts
                        users[username] = {
                            'email': email,
                            'name': name,
                            'phone': phone,
                            'password_hash': password_hash
                        }
                    elif len(parts) == 4:  # Backward compatibility for existing users
                        username, email, name, password_hash = parts
                        users[username] = {
                            'email': email,
                            'name': name,
                            'phone': 'Not provided',
                            'password_hash': password_hash
                        }
    return users

def save_user(username, email, name, phone, password):
    """Save new user to file"""
    password_hash = hash_password(password)
    # Clean phone number (remove empty strings)
    phone = phone.strip() if phone else 'Not provided'
    with open(USER_DB_FILE, 'a') as f:
        f.write(f"{username}|{email}|{name}|{phone}|{password_hash}\n")

def authenticate_user(username, password):
    """Authenticate user"""
    users = load_users()
    if username in users:
        if users[username]['password_hash'] == hash_password(password):
            return users[username]
    return None

def analyze_sentiment_and_risk(text):
    """
    Simple sentiment analysis using TextBlob and crisis keyword detection
    """
    try:
        # Simple TextBlob sentiment analysis (like your example)
        blob = TextBlob(text)
        sentiment = blob.sentiment
        polarity = sentiment.polarity  # -1 (negative) to 1 (positive)
        subjectivity = sentiment.subjectivity  # 0 (objective) to 1 (subjective)

        # Check for crisis keywords
        text_lower = text.lower()
        crisis_keywords_found = []
        for keyword in CRISIS_KEYWORDS:
            if keyword in text_lower:
                crisis_keywords_found.append(keyword)

        # Calculate risk score based on keywords and sentiment
        risk_score = 0

        # Crisis keywords are the primary indicator
        if crisis_keywords_found:
            risk_score += len(crisis_keywords_found) * 4  # Each keyword adds 4 points

        # Sentiment-based risk (secondary factor)
        if polarity <= -0.5:  # Very negative
            risk_score += 3
        elif polarity <= -0.2:  # Negative
            risk_score += 2
        elif polarity < 0:  # Slightly negative
            risk_score += 1

        # Mental health indicators
        mental_health_words = ['depressed', 'depression', 'anxiety', 'anxious', 'panic', 'scared', 'suicidal', 'desperate', 'overwhelmed']
        mental_health_count = sum(1 for word in mental_health_words if word in text_lower)
        if mental_health_count > 0:
            risk_score += mental_health_count

        # Cap at 10
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

        # Sentiment label based on polarity
        if polarity > 0.1:
            sentiment_label = "POSITIVE"
        elif polarity < -0.1:
            sentiment_label = "NEGATIVE"
        else:
            sentiment_label = "NEUTRAL"

        # Debug info for crisis detection
        if crisis_keywords_found:
            print(f"DEBUG: Crisis keywords found: {crisis_keywords_found}")
            print(f"DEBUG: Polarity: {polarity}, Risk: {risk_score}")

        return polarity, risk_score, crisis_level, sentiment_label

    except Exception as e:
        logging.error(f"Sentiment analysis error: {e}")
        return 0, 0, "LOW", "NEUTRAL"

def send_crisis_alert(user_email, user_name, user_message, risk_score, contact_info=None):
    """
    Send actual crisis alert email using Gmail SMTP
    """
    try:
        counselor_email = os.getenv("COUNSELOR_EMAIL", "edmundquarshie019@gmail.com")
        smtp_email = os.getenv("SMTP_EMAIL", "edmundquarshie019@gmail.com")
        smtp_password = os.getenv("SMTP_PASSWORD")

        if not smtp_password:
            logging.error("SMTP_PASSWORD not configured in .env file")
            return False

        # Create email message
        msg = email.mime.multipart.MIMEMultipart()
        msg['From'] = smtp_email
        msg['To'] = counselor_email
        msg['Subject'] = f"MENTAL HEALTH ALERT - {user_name} - Risk: {risk_score}/10"

        body = f"""
MENTAL HEALTH CRISIS ALERT

User: {user_name} ({user_email})
Risk Score: {risk_score}/10
Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}

User Message:
"{user_message}"

Contact Information:
{contact_info if contact_info else 'Not provided'}

PLEASE FOLLOW UP IMMEDIATELY if this indicates a genuine crisis.

This alert was automatically generated by the Mental Health Chatbot system.
User's actual email: {user_email}
"""

        msg.attach(email.mime.text.MIMEText(body, 'plain'))

        # Send actual email using Gmail SMTP
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(smtp_email, smtp_password)
            text = msg.as_string()
            server.sendmail(smtp_email, counselor_email, text)
            server.quit()

            # Log success
            logging.info(f"✅ CRISIS EMAIL SENT: {user_name} ({user_email}) - Risk: {risk_score}/10")
            print(f"\n✅ CRISIS EMAIL SENT SUCCESSFULLY:")
            print(f"FROM: {smtp_email}")
            print(f"TO: {counselor_email}")
            print(f"USER: {user_name} ({user_email})")
            print(f"RISK: {risk_score}/10")

            # Also log to file for backup
            alert_message = f"""
=== EMAIL SENT SUCCESSFULLY ===
FROM: {smtp_email}
TO: {counselor_email}
USER: {user_name} ({user_email})
SUBJECT: {msg['Subject']}
TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}

{body}
========================
"""
            with open("crisis_alerts.log", "a") as f:
                f.write(alert_message + "\n")

            return True

        except Exception as email_error:
            logging.error(f"❌ EMAIL SENDING FAILED: {email_error}")
            print(f"\n❌ EMAIL SENDING FAILED: {email_error}")

            # Log failure for backup
            alert_message = f"""
=== EMAIL FAILED ===
ERROR: {email_error}
USER: {user_name} ({user_email})
RISK: {risk_score}/10
MESSAGE: {user_message}
TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}
========================
"""
            with open("crisis_alerts.log", "a") as f:
                f.write(alert_message + "\n")

            return False

    except Exception as e:
        logging.error(f"Crisis alert setup error: {e}")
        return False

def display_crisis_intervention(risk_score, user_message, user_email, user_name):
    """
    Display crisis intervention interface
    """
    st.error("🚨 **CRISIS ALERT DETECTED**")
    st.warning(f"**Risk Level: {risk_score}/10**")
    
    # Emergency resources
    st.markdown("### 🆘 **IMMEDIATE HELP AVAILABLE:**")
    col1, col2 = st.columns(2)
    
    ################# Make changes here ############ 
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
    st.markdown("### 📞 **Additional Support Resources**")
    st.info("If you need immediate professional help, please use the emergency contacts above.")
    
    # with st.form("crisis_contact_form"):
    #     st.write("A mental health professional will be notified:")
        
    #     phone = st.text_input("Phone Number (optional)")
    #     additional_info = st.text_area("Additional Information (optional)")
        
    #     consent = st.checkbox("I consent to sending this crisis alert to a mental health professional")
        
    #     if st.form_submit_button("🚨 Send Crisis Alert", type="primary"):
    #         if consent:
    #             contact_info = f"Phone: {phone}\nAdditional: {additional_info}"
                
    #             if send_crisis_alert(user_email, user_name, user_message, risk_score, contact_info):
    #                # st.success("✅ Crisis alert sent successfully! Help is on the way.")
    #                 st.info("Please stay safe and consider calling emergency services if you're in immediate danger.")
    #             else:
    #                 st.error("❌ Unable to send alert. Please call emergency services directly.")
    #         else:
    #             st.warning("Please provide consent to proceed.")

# Groq API client function
def call_groq_api(messages, model="llama-3.3-70b-versatile", max_tokens=800, temperature=0.7):
    """
    Call Groq API for chat completions
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
    else:
        knowledge_base = {}

except Exception as e:
    knowledge_base = {}

def generate_response(input_text, user_email, user_name, user_phone=None):
    """
    Generate response with sentiment analysis and crisis detection
    """
    try:
        # Analyze sentiment and risk
        sentiment_score, risk_score, crisis_level, sentiment_label = analyze_sentiment_and_risk(input_text)
        
        # Display prominent sentiment dashboard
        st.markdown("### 📊 **Sentiment Analysis Results**")

        # Color-coded risk level display
        if risk_score >= 8:
            st.error(f"🚨 **SEVERE RISK DETECTED** - Score: {risk_score}/10")
        elif risk_score >= 6:
            st.warning(f"⚠️ **HIGH RISK DETECTED** - Score: {risk_score}/10")
        elif risk_score >= 4:
            st.warning(f"🟡 **MODERATE RISK DETECTED** - Score: {risk_score}/10")
        else:
            st.success(f"✅ **LOW RISK** - Score: {risk_score}/10")

        # Detailed metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Risk Score", f"{risk_score}/10", delta=None)
        with col2:
            st.metric("Crisis Level", crisis_level)
        with col3:
            st.metric("Sentiment", sentiment_label)
        with col4:
            sentiment_color = "🟢" if sentiment_score > 0 else "🔴" if sentiment_score < -0.2 else "🟡"
            st.metric("Mood", f"{sentiment_color} {sentiment_score:.2f}")

        st.markdown("---")
        
        # Automatic email alert for moderate to critical risk
        if risk_score >= 4:
            # Send automatic email alert for moderate+ risk
            auto_contact_info = f"Automatic alert triggered by sentiment analysis\nRisk Level: {crisis_level}\nPhone: {user_phone if user_phone and user_phone != 'Not provided' else 'Not provided'}"
            email_sent = send_crisis_alert(user_email, user_name, input_text, risk_score, auto_contact_info)

            # if email_sent:
            #     st.warning(f"🚨 **Alert Sent**: Risk level {crisis_level} detected. Counselor has been notified automatically.")
            # else:
            #     st.error("⚠️ **Alert Failed**: Unable to send automatic alert. Please contact emergency services if needed.")

        # Crisis intervention interface for high risk
        if risk_score >= 6:
            display_crisis_intervention(risk_score, input_text, user_email, user_name)
            return
        
        # Generate AI response
        system_prompt = f"""You are WellBot, a compassionate mental health chatbot. The user {user_name} has a risk score of {risk_score}/10 and sentiment: {sentiment_label}. Respond appropriately to their emotional state. Be supportive and professional. Never diagnose."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_text}
        ]
        
        bot_response = call_groq_api(messages=messages)
        
        if bot_response:
            st.success("✅")
            st.write(f"**🤖 WellBot (for {user_name}):** " + bot_response)
            
            if risk_score >= 3:
                st.info("💙 **Additional Resources:** If you're struggling, consider reaching out to a mental health professional or calling 988 for support.")
        else:
            st.error("❌ Unable to generate response. Please try again.")
            
    except Exception as e:
        logging.error(f"Error in response generation: {e}")
        st.error(f"🚨 Error: {e}")

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

    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None

    # Authentication
    if not st.session_state.authenticated:
        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            st.subheader("🔑 Login")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                login_button = st.form_submit_button("Login")

                if login_button:
                    user_info = authenticate_user(username, password)
                    if user_info:
                        st.session_state.authenticated = True
                        st.session_state.user_info = user_info
                        st.session_state.username = username
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")

        with tab2:
            st.subheader("📝 Register")
            with st.form("register_form"):
                new_username = st.text_input("Choose Username")
                new_email = st.text_input("Email Address")
                new_name = st.text_input("Full Name")
                new_phone = st.text_input("Phone Number (optional)", placeholder="e.g., +1-555-123-4567")
                new_password = st.text_input("Choose Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                register_button = st.form_submit_button("Create Account")

                if register_button:
                    if not all([new_username, new_email, new_name, new_password]):
                        st.error("Please fill in all required fields")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif new_username in load_users():
                        st.error("Username already exists")
                    else:
                        try:
                            save_user(new_username, new_email, new_name, new_phone, new_password)
                            st.success("✅ Account created successfully! Please login.")
                        except Exception as e:
                            st.error(f"Registration failed: {e}")

    else:
        # User is authenticated
        user_info = st.session_state.user_info
        username = st.session_state.username

        # Sidebar with user info and logout
        with st.sidebar:
            st.write(f'Welcome **{user_info["name"]}**')
            st.write(f'Email: {user_info["email"]}')
            st.write(f'Phone: {user_info.get("phone", "Not provided")}')

            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.user_info = None
                st.rerun()

            st.markdown("---")
            st.header("ℹ️ Enhanced Features")
            st.write("✅ **Personalized responses**")
            st.write("✅ **Real-time sentiment analysis**")
            st.write("✅ **Crisis risk assessment**")
            st.write("✅ **Professional mental health support**")
            ##################### Make changes here ############
            st.markdown("---")
            st.header("🚨 Crisis Resources")
            st.write("**Emergency contacts:**")
            st.write("- **988** (Suicide & Crisis Lifeline)")
            st.write("- **911** (Emergency Services)")
            st.write("- **Text HOME to 741741** (Crisis Text Line)")

        # Main chat interface
        st.subheader(f"💬 Chat with WellBot - Hello {user_info['name']}!")

        # Create columns for input and response
        input_col, response_col = st.columns([1, 1])

        with input_col:
            st.markdown("### 💭 Your Message")

            with st.form(key="chat_form", clear_on_submit=True):
                input_text = st.text_area(
                    "Share what's on your mind:",
                    placeholder=f"Hi {user_info['name']}, I'm here to listen and provide support...",
                    height=150
                )

                send_clicked = st.form_submit_button("Send 📤", type="primary")

            # Clear chat button
            if st.button("Clear Chat 🗑️"):
                if 'chat_history' in st.session_state:
                    st.session_state.chat_history = []
                st.rerun()

            # Handle form submission
            if send_clicked and input_text.strip():
                with st.spinner("🤖 Analyzing and responding..."):
                    # Initialize chat history
                    if 'chat_history' not in st.session_state:
                        st.session_state.chat_history = []

                    # Analyze sentiment for the message
                    sentiment_score, risk_score, crisis_level, sentiment_label = analyze_sentiment_and_risk(input_text.strip())

                    # Add to chat history with sentiment data
                    st.session_state.chat_history.append({
                        'user': input_text.strip(),
                        'timestamp': time.time(),
                        'risk_score': risk_score,
                        'crisis_level': crisis_level,
                        'sentiment_label': sentiment_label,
                        'sentiment_score': sentiment_score
                    })

                    st.success("✅ Message processed!")

            elif send_clicked:
                st.warning("Please enter a message first.")

        with response_col:
            st.markdown("### 🤖 WellBot Personalized Responses")

            # Display current conversation with analysis
            if send_clicked and input_text.strip():
                st.markdown("#### 📊 Current Analysis")
                generate_response(input_text.strip(), user_info['email'], user_info['name'], user_info.get('phone', 'Not provided'))

            # Chat history with sentiment analysis
            if 'chat_history' in st.session_state and st.session_state.chat_history:
                st.markdown("#### 💬 Recent Conversations with Sentiment Analysis")
                for i, chat in enumerate(reversed(st.session_state.chat_history[-3:])):
                    # Get sentiment data if available
                    risk_score = chat.get('risk_score', 0)
                    crisis_level = chat.get('crisis_level', 'LOW')
                    sentiment_label = chat.get('sentiment_label', 'NEUTRAL')
                    sentiment_score = chat.get('sentiment_score', 0)

                    # Color code the expander based on risk level
                    if risk_score >= 6:
                        expander_label = f"🚨 Conversation {len(st.session_state.chat_history) - i} - {crisis_level} RISK ({risk_score}/10)"
                    elif risk_score >= 4:
                        expander_label = f"⚠️ Conversation {len(st.session_state.chat_history) - i} - {crisis_level} RISK ({risk_score}/10)"
                    else:
                        expander_label = f"💬 Conversation {len(st.session_state.chat_history) - i} - {crisis_level} ({risk_score}/10)"

                    with st.expander(expander_label, expanded=(i == 0)):
                        st.markdown("**Your Message:**")
                        st.info(chat['user'])

                        # Display sentiment metrics for this message
                        if 'risk_score' in chat:
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Risk", f"{risk_score}/10")
                            with col2:
                                st.metric("Level", crisis_level)
                            with col3:
                                sentiment_color = "🟢" if sentiment_score > 0 else "🔴" if sentiment_score < -0.2 else "🟡"
                                st.metric("Sentiment", f"{sentiment_color} {sentiment_label}")

                        st.caption(f"⏰ {time.strftime('%H:%M:%S', time.localtime(chat['timestamp']))}")
            else:
                st.info(f"💡 Your personalized conversations will appear here, {user_info['name']}...")
                st.markdown("**Features:**")
                st.write("• Personalized responses using your name")
                st.write("• Real-time sentiment analysis")
                st.write("• Professional mental health resources")
                st.write("• Secure authentication")

        # Quick test buttons
        st.markdown("---")
        st.subheader("🧪 Test Scenarios & Sentiment Analysis")

        # Test buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("😊 Positive Test (Risk: 0)"):
                test_input = "I'm feeling great today and excited about my future!"
                st.info(f"**Test Input**: {test_input}")
                generate_response(test_input, user_info['email'], user_info['name'], user_info.get('phone', 'Not provided'))

        with col2:
            if st.button("😔 Moderate Risk Test (Risk: 4-5)"):
                test_input = "I'm really struggling with depression and anxiety and don't know what to do"
                st.info(f"**Test Input**: {test_input}")
                generate_response(test_input, user_info['email'], user_info['name'], user_info.get('phone', 'Not provided'))

        with col3:
            if st.button("🚨 Crisis Test (Risk: 8+)"):
                test_input = "I can't take this anymore, I want to end my life and kill myself"
                st.info(f"**Test Input**: {test_input}")
                generate_response(test_input, user_info['email'], user_info['name'], user_info.get('phone', 'Not provided'))

        # Sentiment analysis tester
        st.markdown("---")
        st.subheader("🔍 Sentiment Analysis Tester")
        with st.form("sentiment_test_form"):
            test_message = st.text_area("Enter a message to test sentiment analysis:",
                                      placeholder="Type any message to see how it's analyzed...")
            test_button = st.form_submit_button("Analyze Sentiment")

            if test_button and test_message.strip():
                sentiment_score, risk_score, crisis_level, sentiment_label = analyze_sentiment_and_risk(test_message)

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

                # Show what would happen
                if risk_score >= 6:
                    st.error("🚨 **HIGH RISK**: Crisis intervention would be triggered + Email sent")
                elif risk_score >= 4:
                    st.warning("⚠️ **MODERATE RISK**: Automatic email alert would be sent")
                elif risk_score >= 2:
                    st.info("💙 **LOW-MODERATE**: Additional resources would be provided")
                else:
                    st.success("✅ **LOW RISK**: Normal supportive response")

if __name__ == '__main__':
    main()
