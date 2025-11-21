import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
import time
import random

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Simplotel Smart Concierge", page_icon="🏨", layout="wide")

# --- SESSION STATE SETUP (The Memory) ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [("Bot", "System Online. Say 'Book a room' to start.")]
if 'booking_step' not in st.session_state:
    st.session_state.booking_step = 0  # 0=Idle
if 'booking_data' not in st.session_state:
    st.session_state.booking_data = {}  # Stores user choices

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(to right, #141e30, #243b55);
        color: white;
    }
    .user-msg {
        background-color: #0078ff;
        color: white;
        padding: 12px 18px;
        border-radius: 15px 15px 0px 15px;
        margin: 10px 0;
        text-align: right;
        float: right;
        clear: both;
        max-width: 70%;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }
    .bot-msg {
        background-color: #333;
        color: #e0e0e0;
        padding: 12px 18px;
        border-radius: 15px 15px 15px 0px;
        margin: 10px 0;
        text-align: left;
        float: left;
        clear: both;
        max-width: 70%;
        border-left: 4px solid #00ff88;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }
    .status-box {
        padding: 20px;
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


# --- CONVERSATION ENGINE ---
def process_conversation(text):
    text = text.lower()
    step = st.session_state.booking_step
    response = "I didn't catch that."

    # Global Exit Command
    if "cancel" in text or "stop" in text:
        st.session_state.booking_step = 0
        st.session_state.booking_data = {}
        return "Booking cancelled. How else can I help you?"

    # --- STEP 0: INITIAL REQUEST ---
    if step == 0:
        if "book" in text:
            st.session_state.booking_step = 1
            return "That's great! I can help you find the perfect room. First, how many members will be staying?"
        elif "price" in text:
            return "Our prices start at $100 for standard and $300 for suites."
        elif "hello" in text:
            return "Hello! Welcome to Simplotel. Would you like to book a room?"
        else:
            return "I am listening. Say 'Book a room' to begin."

    # --- STEP 1: MEMBERS ---
    elif step == 1:
        # Extract numbers
        import re
        nums = re.findall(r'\d+', text)

        # Handle word numbers (basic)
        if "one" in text:
            num = "1"
        elif "two" in text:
            num = "2"
        elif "three" in text:
            num = "3"
        elif "four" in text:
            num = "4"
        elif nums:
            num = nums[0]
        else:
            return "Could you please repeat the number of people?"

        st.session_state.booking_data['members'] = num
        st.session_state.booking_step = 2
        return f"Okay, {num} guests. Do you prefer an AC room or Non-AC?"

    # --- STEP 2: AC / NON-AC ---
    elif step == 2:
        if "non" in text:
            st.session_state.booking_data['ac'] = "Non-AC"
            st.session_state.booking_step = 3
            return "Non-AC noted. Now, would you like a room with a Balcony or direct Pool Access?"
        elif "ac" in text:
            st.session_state.booking_data['ac'] = "AC"
            st.session_state.booking_step = 3
            return "Cool choice! An AC room. Would you prefer a Balcony or Pool Access?"
        else:
            return "Please specify: AC or Non-AC?"

    # --- STEP 3: BALCONY / POOL ---
    elif step == 3:
        if "pool" in text:
            st.session_state.booking_data['feature'] = "Pool Access"
        elif "balcony" in text:
            st.session_state.booking_data['feature'] = "Balcony"
        else:
            st.session_state.booking_data['feature'] = "Standard View"

        st.session_state.booking_step = 4
        return "Got it. Last question: Do you want a Sea/Beach View? (Yes or No)"

    # --- STEP 4: BEACH VIEW ---
    elif step == 4:
        if "yes" in text or "sure" in text or "beach" in text:
            st.session_state.booking_data['view'] = "Beach View"
            price = "5000"
        else:
            st.session_state.booking_data['view'] = "Garden View"
            price = "3500"

        # --- FINALIZE ---
        data = st.session_state.booking_data
        summary = (f"Perfect! I have confirmed a {data['ac']} room with {data['feature']} "
                   f"and {data['view']} for {data['members']} people. "
                   f"Total price is {price} rupees. Should I proceed?")

        st.session_state.booking_step = 5  # Waiting for final yes
        return summary

    # --- STEP 5: CONFIRMATION ---
    elif step == 5:
        if "yes" in text or "proceed" in text or "ok" in text:
            st.session_state.booking_step = 0  # Reset
            return "Booking Confirmed! Sending details to your email. Thank you for choosing Simplotel!"
        else:
            st.session_state.booking_step = 0
            return "Booking cancelled."

    return "I didn't understand."


# --- AUDIO FUNCTIONS ---
def speak_text(text):
    """Converts text to audio and plays it"""
    try:
        tts = gTTS(text=text, lang='en')
        filename = f"temp_response_{int(time.time())}.mp3"
        tts.save(filename)

        # Display Audio Player
        audio_file = open(filename, "rb")
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        audio_file.close()

        # Clean up
        os.remove(filename)
    except Exception as e:
        st.error(f"Audio Error: {e}")


def listen_mic():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        status_container.info("🎧 Listening... (Speak now!)")
        try:
            # Fast adjustments
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
            status_container.success("Processing...")
            return r.recognize_google(audio)
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception as e:
            st.error(f"Mic Error: {e}")
            return None


# --- UI LAYOUT ---
st.title("🏨 Simplotel Interactive Concierge")

# Sidebar for State Visualization
with st.sidebar:
    st.header("Current Booking Status")
    if st.session_state.booking_data:
        for key, value in st.session_state.booking_data.items():
            st.success(f"**{key.capitalize()}:** {value}")
    else:
        st.info("No booking in progress.")

    st.markdown("---")
    st.write(f"Debug: Step {st.session_state.booking_step}")

# Chat Container
chat_container = st.container()
with chat_container:
    for role, text in st.session_state.chat_history:
        if role == "User":
            st.markdown(f"<div class='user-msg'>{text}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-msg'>{text}</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div style='height: 50px'></div>", unsafe_allow_html=True)
status_container = st.empty()
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🎙️ Click to Speak", use_container_width=True):
        user_input = listen_mic()

        if user_input:
            # 1. Update Chat with User Input
            st.session_state.chat_history.append(("User", user_input))

            # 2. Process Logic
            bot_response = process_conversation(user_input)

            # 3. Update Chat with Bot Response
            st.session_state.chat_history.append(("Bot", bot_response))

            # 4. Rerun to show text immediately, then play audio
            st.rerun()

# Auto-play audio if the last message was from Bot (and brand new)
if st.session_state.chat_history and st.session_state.chat_history[-1][0] == "Bot":
    # Use a simple hash check or length check to prevent re-playing on every interaction
    # For simplicity here, we rely on the flow.
    last_msg = st.session_state.chat_history[-1][1]
    # Only speak if we haven't just spoken it (Checking mechanism usually requires IDs)
    # We call speak_text here.
    speak_text(last_msg)