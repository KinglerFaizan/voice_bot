import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import time
import base64

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FRIDAY AI",
    page_icon="🧿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. SESSION STATE ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant",
         "content": "Hello. I am Friday. I am online and ready to assist you. Would you like to book a room or do you have a query?"}
    ]
if 'booking_step' not in st.session_state:
    st.session_state.booking_step = 0
if 'booking_data' not in st.session_state:
    st.session_state.booking_data = {"guests": "TBD", "type": "TBD", "view": "TBD"}

# --- 3. FUTURISTIC STYLING ---
st.markdown("""
<style>
    /* Background: Abstract Dark Network */
    .stApp {
        background: linear-gradient(to bottom, rgba(0,0,0,0.9), rgba(20,20,40,0.95)), 
                    url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop');
        background-size: cover;
        color: #00ffff;
        font-family: 'Orbitron', sans-serif; /* Sci-fi Font fallback */
    }

    /* Chat Bubbles */
    .stChatMessage {
        background: rgba(0, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 255, 0.2);
        border-radius: 12px;
        backdrop-filter: blur(8px);
    }
    div[data-testid="chatAvatarIcon-assistant"] { background-color: #00ffff !important; color: black !important; }
    div[data-testid="chatAvatarIcon-user"] { background-color: #ff0055 !important; }

    /* THE PULSING ORB */
    div.stButton > button:first-child {
        background: radial-gradient(circle, #00ffff 0%, #004444 100%);
        border: 2px solid #00ffff;
        border-radius: 50%;
        height: 120px;
        width: 120px;
        color: transparent;
        box-shadow: 0 0 30px #00ffff, 0 0 50px #00ffff inset;
        animation: pulse 3s infinite;
        margin: 0 auto;
        display: block;
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.1);
        box-shadow: 0 0 60px #00ffff, 0 0 100px #00ffff inset;
    }
    div.stButton > button:first-child:active {
        border-color: #ff0055;
        box-shadow: 0 0 60px #ff0055, 0 0 100px #ff0055 inset;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 255, 255, 0.7); }
        70% { box-shadow: 0 0 0 20px rgba(0, 255, 255, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 255, 255, 0); }
    }

    /* Hide standard UI elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- 4. AUDIO ENGINE (The "Beautiful Voice") ---
def play_friday_voice(text):
    """
    Plays audio using gTTS with a British accent (co.uk)
    which sounds more like a refined AI assistant.
    """
    try:
        audio_file = "friday_speech.mp3"
        # tld='co.uk' gives a British accent. tld='us' is American.
        tts = gTTS(text=text, lang='en', tld='co.uk')
        tts.save(audio_file)

        # Native Streamlit Player (Hidden but Autoplays)
        with open(audio_file, "rb") as f:
            audio_bytes = f.read()

        # Unique key ensures the player reloads on new text
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
    except Exception as e:
        st.warning(f"Voice Output Error: {e}")


# --- 5. CONVERSATION LOGIC ---
def get_ai_response(user_text):
    text = user_text.lower()
    step = st.session_state.booking_step

    # EXIT COMMANDS
    if any(x in text for x in ["bye", "exit", "quit"]):
        return "Shutting down. Have a lovely day."
    if any(x in text for x in ["reset", "cancel", "restart"]):
        st.session_state.booking_step = 0
        return "System reset. How can I help you now?"

    # --- BOOKING FLOW ---
    if step == 0:
        if any(x in text for x in ["book", "room", "reservation", "stay"]):
            st.session_state.booking_step = 1
            return "Certainly. I can arrange that. How many guests will be staying?"
        elif any(x in text for x in ["hi", "hello", "friday"]):
            return "Hello. I am listening. Would you like to make a reservation?"
        return "I am ready. Please tell me if you want to book a room."

    elif step == 1:  # Guests
        import re
        nums = re.findall(r'\d+', text)
        words = {"one": "1", "two": "2", "three": "3", "four": "4"}
        for w, d in words.items():
            if w in text: nums.append(d)

        if nums:
            st.session_state.booking_data['guests'] = nums[0]
            st.session_state.booking_step = 2
            return f"{nums[0]} guests registered. Would you prefer an AC or Non-AC suite?"
        return "I didn't catch the number. How many guests?"

    elif step == 2:  # Type
        if "non" in text:
            st.session_state.booking_data['type'] = "Non-AC"
            st.session_state.booking_step = 3
            return "Non-AC selected. Would you like a Balcony or Pool Access?"
        elif "ac" in text:
            st.session_state.booking_data['type'] = "AC"
            st.session_state.booking_step = 3
            return "AC suite selected. Excellent choice. Would you like a Balcony or Pool Access?"
        return "Please specify: AC or Non-AC?"

    elif step == 3:  # Feature
        if "pool" in text:
            st.session_state.booking_data['view'] = "Pool Access"
            price = "5000"
        else:
            st.session_state.booking_data['view'] = "Balcony"
            price = "3500"

        st.session_state.booking_step = 4
        return f"I have configured a {st.session_state.booking_data['type']} suite with {st.session_state.booking_data['view']}. The total is {price} credits. Shall I confirm this reservation?"

    elif step == 4:  # Confirm
        if any(x in text for x in ["yes", "confirm", "ok", "sure"]):
            st.balloons()
            st.session_state.booking_step = 0
            return "Authorization Verified. Your reservation is confirmed. I have sent the details to your device. Goodbye."
        else:
            st.session_state.booking_step = 0
            return "Authorization denied. Cancelling request."

    return "I am not sure I understood. Could you rephrase that?"


# --- 6. UI LAYOUT ---

# Header
c1, c2 = st.columns([1, 10])
with c1:
    st.markdown("## 🧿")
with c2:
    st.markdown("## F.R.I.D.A.Y. \n *Simplotel AI*")

st.divider()

# Chat Display
chat_container = st.container(height=400)
with chat_container:
    for msg in st.session_state.chat_history:
        with st.chat_message(msg['role']):
            st.write(msg['content'])

# Spacer
st.markdown("<br>", unsafe_allow_html=True)

# --- VOICE INTERFACE ---
c1, c2, c3 = st.columns([1, 1, 1])
with c2:
    st.write("**TAP THE ORB TO SPEAK**")

    # THE VOICE INPUT
    voice_text = speech_to_text(
        language='en',
        start_prompt="●",
        stop_prompt="■",
        just_once=True,
        key='orb'
    )

# --- TEXT INTERFACE (Fallback) ---
text_text = st.chat_input("Or type commands here...")

# --- UNIFIED PROCESSING ---
user_input = voice_text if voice_text else text_text

if user_input:
    # 1. Add User Input
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # 2. Get Bot Response
    bot_reply = get_ai_response(user_input)
    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

    # 3. Refresh to show text and trigger audio
    st.rerun()

# --- AUTO-PLAY LOGIC ---
# This runs automatically at the end of the script.
# If the last message is from the bot, it generates and plays the audio.
if st.session_state.chat_history:
    last_msg = st.session_state.chat_history[-1]
    if last_msg['role'] == 'assistant':
        # Create a unique key based on content length + time to force reload
        play_friday_voice(last_msg['content'])