import os
import pandas as pd
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import logging
import time

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

# Groq API client function
def call_groq_api(messages, model="llama-3.3-70b-versatile", max_tokens=300, temperature=0.7):
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
    # Try different possible locations for the CSV file
    csv_paths = [
        "AI_Mental_Health.csv",  # Same directory
        "../AI_Mental_Health.csv",  # Parent directory
        "Personalized_Mental_Healthcare-Chatbot-main/AI_Mental_Health.csv"  # Full path
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
        # Create a knowledge base from the dataset
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
    st.info("Expected locations: AI_Mental_Health.csv in the same folder as the app")
    knowledge_base = {}
except Exception as e:
    st.error(f"❌ Error loading mental health dataset: {e}")
    knowledge_base = {}

# Voice recognition using Groq Whisper (improved)
def get_voice_input():
    """Get voice input from user using Groq Whisper - Streamlit compatible"""
    try:
        import speech_recognition as sr
        import tempfile
        import os

        if not groq_client:
            st.error("❌ Groq client not available for voice transcription.")
            return None

        r = sr.Recognizer()

        with sr.Microphone() as source:
            st.info("🎤 Adjusting for ambient noise... Please wait.")
            r.adjust_for_ambient_noise(source, duration=1)

            # Lower the energy threshold for more sensitive detection
            r.energy_threshold = max(50, r.energy_threshold * 0.5)
            st.info(f"🔧 Energy threshold set to: {r.energy_threshold:.1f}")

            st.success("🎤 Ready! Please speak LOUDLY and CLEARLY (you have 15 seconds)...")
            st.warning("💡 Speak directly into your microphone!")

            try:
                audio = r.listen(source, timeout=15, phrase_time_limit=20)
                st.info("🔄 Processing your speech with Groq Whisper...")

                # Save audio to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(audio.get_wav_data())
                    tmp_file_path = tmp_file.name

                try:
                    # Use Groq Whisper for transcription
                    with open(tmp_file_path, "rb") as audio_file:
                        transcription = groq_client.audio.transcriptions.create(
                            file=audio_file,
                            model="whisper-large-v3-turbo",
                            response_format="text"
                        )

                    # Clean up temporary file
                    os.unlink(tmp_file_path)

                    if transcription and transcription.strip():
                        st.success(f"✅ Whisper transcribed: {transcription}")
                        return transcription.strip()
                    else:
                        st.warning("🤷 No speech detected in audio.")
                        return None

                except Exception as whisper_error:
                    st.error(f"❌ Whisper transcription error: {whisper_error}")
                    # Fallback to Google Speech Recognition
                    st.info("🔄 Falling back to Google Speech Recognition...")
                    try:
                        query = r.recognize_google(audio)
                        st.success(f"✅ Google recognized: {query}")
                        return query
                    except:
                        st.warning("🤷 Could not transcribe audio with either service.")
                        return None
                finally:
                    # Ensure temp file is cleaned up
                    if os.path.exists(tmp_file_path):
                        os.unlink(tmp_file_path)

            except sr.WaitTimeoutError:
                st.error("⏰ No speech detected within 15 seconds.")
                st.info("💡 **Troubleshooting Tips:**")
                st.write("• **Speak louder** - Your microphone might need more volume")
                st.write("• **Get closer** - Move closer to your microphone")
                st.write("• **Check microphone** - Ensure it's not muted")
                st.write("• **Try again** - Sometimes it takes a few attempts")
                st.write("• **Test microphone** - Try speaking in another app first")
                return None

    except ImportError as e:
        st.error("❌ Speech recognition not available.")
        st.info("Please install required packages:")
        st.code("pip install SpeechRecognition pyaudio")
        return None
    except OSError as e:
        if "PyAudio" in str(e):
            st.error("❌ PyAudio not found. Voice input requires PyAudio for microphone access.")
            st.info("Install PyAudio:")
            st.code("pip install pyaudio")
            st.info("If installation fails on Windows, try:")
            st.code("pip install pipwin\npipwin install pyaudio")
        else:
            st.error(f"❌ Audio system error: {e}")
        return None
    except Exception as e:
        error_msg = str(e)
        if "PyAudio" in error_msg:
            st.error("❌ PyAudio installation issue detected.")
            st.info("Try installing PyAudio:")
            st.code("pip install pyaudio")
        elif "microphone" in error_msg.lower():
            st.error("❌ Microphone access issue.")
            st.info("Please check that:")
            st.write("• Your microphone is connected and working")
            st.write("• Browser has microphone permissions")
            st.write("• No other application is using the microphone")
        else:
            st.error(f"❌ Voice recognition error: {error_msg}")
        return None

# Define function for generating responses
def generate_response(input_text):
    try:
        # Check if we have a direct match in our knowledge base first
        relevant_context = ""
        user_input_lower = input_text.lower()

        # Search for relevant information in knowledge base
        direct_matches = []
        for question, answer in knowledge_base.items():
            if any(word in question for word in user_input_lower.split()):
                direct_matches.append((question, answer))
                relevant_context += f"Q: {question}\nA: {answer}\n\n"

        # TEMPORARILY DISABLED FOR GROQ API TESTING
        # Force all queries to use Groq API instead of knowledge base
        if False:  # len(direct_matches) >= 1:
            st.write("**🤖 Mental Health Assistant:** Based on our mental health knowledge base:")

            # Show the most relevant answer
            best_match = direct_matches[0]
            st.write(f"**Q:** {best_match[0].title()}")
            st.write(f"**A:** {best_match[1]}")

            # Add supportive message
            st.write("\n💙 **Additional Support:** Remember that seeking professional help is always a good step when dealing with mental health concerns.")

        else:
            # Only use Grok API if no good knowledge base matches
            # Create a comprehensive mental health focused prompt
            system_prompt = f"""You are WellBot, a compassionate mental health chatbot. Be empathetic, supportive, and encourage professional help when needed. Never diagnose. Provide complete, helpful responses in 2-3 paragraphs. Always finish your thoughts completely and provide actionable advice.

            Context: {relevant_context[:1000] if relevant_context else 'General mental health support'}"""

            # Generate responses using Groq API
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_text}
            ]

            bot_response = call_groq_api(
                messages=messages,
                model="llama-3.3-70b-versatile",
                max_tokens=300,  # Increased for complete responses
                temperature=0.7
            )

            # No character limit - let responses be complete

            if bot_response:
                st.success("✅")
                st.write("**🤖 WellBot :** " + bot_response)
               
            else:
                # Fallback to knowledge base if API fails
                st.warning("🔄 API temporarily unavailable. Using knowledge base...")
                fallback_response = "I'm here to support you. While I'm having technical difficulties, please know that your feelings are valid and seeking help is always a good step."
                if relevant_context:
                    fallback_response += f"\n\n {relevant_context[:200]}..."
                st.write("**🤖 WellBot (Knowledge Base):** " + fallback_response)

        # Show disclaimer
        st.caption("💡 Remember: This is an AI assistant for support and information. For professional help, please consult a qualified mental health professional.")

    except Exception as e:
        error_msg = str(e)
        logging.error(f"Error generating response: {e}")

        # Handle specific API errors
        if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            st.error("🚨 **API Rate Limit Exceeded**")
            st.warning("The Groq API rate limit has been exceeded. Here are some options:")
            st.info("**Immediate Help:**")
            st.write("• Check your Groq account at: https://console.groq.com/")
            st.write("• Verify your API key and usage limits")
            st.write("• Wait a moment and try again (Groq has generous free tier)")
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            st.error("🚨 **API Authentication Error**")
            st.warning("Please check your Groq API key configuration.")
            st.info("**Steps to fix:**")
            st.write("• Verify your GROQ_API_KEY in the .env file")
            st.write("• Get a valid API key from: https://console.groq.com/")
        elif "404" in error_msg or "not found" in error_msg.lower():
            st.error("🚨 **API Endpoint Error**")
            st.warning("The Groq API endpoint may be incorrect or unavailable.")
        else:
            st.error(f"🚨 **API Error:** {error_msg}")

        # Provide fallback response from knowledge base
        if knowledge_base:
            st.info("**Using Knowledge Base Instead:**")
            # Find any relevant info from knowledge base
            user_words = input_text.lower().split()
            for question, answer in list(knowledge_base.items())[:3]:
                if any(word in question for word in user_words):
                    st.write(f"**Q:** {question.title()}")
                    st.write(f"**A:** {answer}")
                    break
            else:
                st.write("Please try asking about specific mental health topics like anxiety, depression, or stress management.")
        else:
            st.error("Sorry, I'm having trouble responding right now. Please try again later.")
            st.info(f"Error details: {error_msg}")

# Function to get bot response without displaying (for chat history)
def get_bot_response(input_text):
    """Get bot response as string without displaying in Streamlit"""
    try:
        # Check if we have a direct match in our knowledge base first
        relevant_context = ""
        user_input_lower = input_text.lower()

        # Search for relevant information in knowledge base
        direct_matches = []
        for question, answer in knowledge_base.items():
            if any(word in question for word in user_input_lower.split()):
                direct_matches.append((question, answer))
                relevant_context += f"Q: {question}\nA: {answer}\n\n"

        # TEMPORARILY DISABLED FOR GROQ API TESTING - Force Groq API
        if False:  # len(direct_matches) >= 1:
            best_match = direct_matches[0]
            return f"Based on our knowledge base:\n\nQ: {best_match[0].title()}\nA: {best_match[1]}\n\n💙 Remember: This is support information. For professional help, please consult a qualified mental health professional."
        else:
            # Use Groq API
            system_prompt = f"""You are WellBot, a compassionate mental health chatbot. Be empathetic, supportive, and encourage professional help when needed. Never diagnose. Provide complete, helpful responses in 2-3 paragraphs. Always finish your thoughts completely and provide actionable advice.

            Context: {relevant_context[:1000] if relevant_context else 'General mental health support'}"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_text}
            ]

            bot_response = call_groq_api(
                messages=messages,
                model="llama-3.3-70b-versatile",
                max_tokens=300,
                temperature=0.7
            )

            # No character limit - let responses be complete

            if bot_response:
                return bot_response
            else:
                # Fallback response
                fallback_response = "I'm here to support you. While I'm having technical difficulties, please know that your feelings are valid and seeking help is always a good step."
                if relevant_context:
                    fallback_response += f"\n\n {relevant_context[:200]}..."
                return fallback_response

    except Exception as e:
        return f"I'm experiencing some technical difficulties right now. Please try again in a moment. If you're in crisis, please contact emergency services or a mental health professional immediately."

# Define main function
def main():
    st.set_page_config(
        page_title="Mental Health Chatbot - Groq Powered",
        page_icon="🧠",
        layout="wide"
    )

    st.title("🧠 Personalized Mental HealthCare Chatbot")
    st.markdown("🎤 **Advanced voice recognition for natural conversations**")
    st.markdown("---")

    # Sidebar with information
    with st.sidebar:
        st.header("ℹ️ About")
        st.write("This chatbot provides mental health support and information.")
        st.write("**Important:** This is not a replacement for professional mental health care.")

        st.header("🚨 Crisis Resources")
        st.write("**If you're in crisis, please reach out immediately:**")
        st.write("- **National Suicide Prevention Lifeline:** 988")
        st.write("- **Crisis Text Line:** Text HOME to 741741")
        st.write("- **Emergency Services:** 911")

    # Main interface
    input_type = st.radio("Select input method:", ("💬 Text", "🎤 Voice"))

    if input_type == "💬 Text":
        # Create two columns for better layout
        input_col, response_col = st.columns([1, 1])

        with input_col:
            st.subheader("💬 Your Message")

            # Use a form to handle input and submission
            with st.form(key="chat_form", clear_on_submit=True):
                input_text = st.text_area(
                    "Share what's on your mind:",
                    placeholder="Type your message here... I'm here to listen and help.",
                    height=150,
                    key="message_input"
                )

                col1, col2 = st.columns([1, 1])
                with col1:
                    send_clicked = st.form_submit_button("Send 📤", type="primary")
                with col2:
                    # Clear chat button outside the form
                    pass

            # Clear chat button outside the form
            if st.button("Clear Chat 🗑️"):
                if 'chat_history' in st.session_state:
                    st.session_state.chat_history = []
                st.rerun()

            # Handle form submission
            if send_clicked and input_text.strip():
                with st.spinner("🤖 Thinking..."):
                    # Initialize chat history if not exists
                    if 'chat_history' not in st.session_state:
                        st.session_state.chat_history = []

                    # Generate response
                    response = get_bot_response(input_text.strip())

                    # Add to chat history
                    st.session_state.chat_history.append({
                        'user': input_text.strip(),
                        'bot': response,
                        'timestamp': time.time()
                    })

                    # Show success message
                    st.success("✅ Message sent!")

            elif send_clicked:
                st.warning("Please enter a message first.")

        with response_col:
            st.subheader("🤖 WellBot Responses")

            # Create a scrollable container for responses
            response_container = st.container()
            with response_container:
                if 'chat_history' in st.session_state and st.session_state.chat_history:
                    # Show conversations in reverse order (newest first)
                    for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5 conversations
                        with st.expander(f"💬 Conversation {len(st.session_state.chat_history) - i}", expanded=(i == 0)):
                            st.markdown("**You:**")
                            st.info(chat['user'])
                            st.markdown("**🤖 WellBot:**")
                            st.success(chat['bot'])
                            st.caption(f"⏰ {time.strftime('%H:%M:%S', time.localtime(chat['timestamp']))}")
                            st.divider()
                else:
                    st.info("� Your conversations will appear here...")
                    st.markdown("**Tips:**")
                    st.write("• Type your message in the left panel")
                    st.write("• Click Send to get a response")
                    st.write("• Responses will appear here instantly")
                    st.write("• Use Clear Chat to start fresh")

    elif input_type == "🎤 Voice":
        st.info("🎤 **Voice Input powered by Groq Whisper Large V3 Turbo**")
        st.markdown("*High-quality speech recognition for mental health conversations*")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎤 Start Recording", type="primary"):
                with st.spinner("🎤 Listening and transcribing with Whisper..."):
                    voice_input = get_voice_input()
                    if voice_input:
                        st.session_state.voice_text = voice_input

        with col2:
            if st.button("Process Voice Input 📤"):
                if hasattr(st.session_state, 'voice_text'):
                    with st.spinner("🤖 Generating response with Groq..."):
                        generate_response(st.session_state.voice_text)
                else:
                    st.warning("Please record your voice first.")

        # Show current voice text if available
        if hasattr(st.session_state, 'voice_text'):
            st.text_area("📝 Transcribed Text:", value=st.session_state.voice_text, height=100, disabled=True)

    # Display conversation history if available
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []

    # Quick help buttons
    st.markdown("---")
    st.subheader("💡 Quick Help Topics")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("😰 Managing Anxiety"):
            generate_response("How can I manage my anxiety?")

    with col2:
        if st.button("😢 Dealing with Depression"):
            generate_response("I'm feeling depressed, what should I do?")

    with col3:
        if st.button("😴 Sleep Issues"):
            generate_response("I'm having trouble sleeping")

if __name__ == '__main__':
    main()



