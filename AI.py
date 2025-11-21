import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import time
import base64

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FRIDAY | AI Core",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. SESSION STATE ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "System Online. I am Friday. How may I assist with your reservation?"}
    ]
if 'booking_step' not in st.session_state:
    st.session_state.booking_step = 0
if 'booking_data' not in st.session_state:
    st.session_state.booking_data = {"guests": "TBD", "type": "TBD", "view": "TBD"}

# --- 3. FUTURISTIC CSS ---
st.markdown("""
<style>
    /* --- BACKGROUND IMAGE --- */
    .stApp {
        background: linear-gradient(to bottom, rgba(0,0,0,0.85), rgba(10,20,40,0.95)), 
                    url('https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #e0e0e0;
    }

    /* --- CHAT BUBBLES --- */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 255, 0.1);
        border-radius: 15px;
        backdrop-filter: blur(5px);
        margin-bottom: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    div[data-testid="chatAvatarIcon-assistant"] { background-color: #00d4ff !important; }
    div[data-testid="chatAvatarIcon-user"] { background-color: #ff0055 !important; }

    /* --- THE GLOWING ORB --- */
    div.stButton > button:first-child {
        background: radial-gradient(circle, #00f2ff 0%, #003344 100%);
        color: transparent;
        border: 2px solid #00f2ff;
        border-radius: 50%;
        height: 110px;
        width: 110px;
        box-shadow: 0 0 25px #00f2ff, 0 0 50px #00f2ff inset;
        transition: all 0.3s ease;
        margin: 0 auto;
        display: block;
        animation: pulse 2s infinite;
    }

    div.stButton > button:first-child:hover {
        transform: scale(1.1);
        box-shadow: 0 0 60px #00f2ff, 0 0 100px #00f2ff inset;
    }

    div.stButton > button:first-child:active {
        background: radial-gradient(circle, #ff0055 0%, #440011 100%);
        border-color: #ff0055;
        box-shadow: 0 0 60px #ff0055;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 242, 255, 0.4); }
        70% { box-shadow: 0 0 0 20px rgba(0, 242, 255, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 242, 255, 0); }
    }

    /* Hide Header/Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- 4. AUDIO ENGINE (HIDDEN PLAYER) ---
def play_friday_voice(text):
    """
    Generates audio and injects a hidden HTML player.
    This removes the visible audio bar while keeping the sound.
    """
    try:
        audio_file = "friday_response.mp3"
        tts = gTTS(text=text, lang='en', tld='co.uk')
        tts.save(audio_file)

        # Read file as bytes
        with open(audio_file, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()

        # Hidden HTML Audio Player with Autoplay
        # style="display:none" hides the player bar
        md = f"""
            <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

        # Cleanup
        os.remove(audio_file)
    except Exception as e:
        st.error(f"Audio System Error: {e}")


# --- 5. INTELLIGENCE CORE ---
def core_logic(text_input):
    text = text_input.lower()
    step = st.session_state.booking_step
    response = "I did not copy that. Please repeat."

    # RESET
    if any(x in text for x in ["reset", "cancel", "restart"]):
        st.session_state.booking_step = 0
        st.session_state.booking_data = {k: "TBD" for k in st.session_state.booking_data}
        return "System reset. Waiting for new instructions."

    # LOGIC FLOW
    if step == 0:
        if any(x in text for x in ["book", "room", "hi", "hello", "friday"]):
            st.session_state.booking_step = 1
            return "Greetings. I can organize your stay. How many guests will be checking in?"
        return "I am Friday. Say 'Book a room' to initialize the reservation protocol."

    elif step == 1:  # GUESTS
        import re
        nums = re.findall(r'\d+', text)
        word_map = {"one": "1", "two": "2", "three": "3", "four": "4"}
        for k, v in word_map.items():
            if k in text: nums.append(v)

        if nums:
            st.session_state.booking_data['guests'] = nums[0]
            st.session_state.booking_step = 2
            return f"{nums[0]} guests registered. Would you prefer an AC or Non-AC configuration?"
        return "Numeric input required. How many guests?"

    elif step == 2:  # TYPE
        if "non" in text:
            st.session_state.booking_data['type'] = "Non-AC"
            st.session_state.booking_step = 3
            return "Non-AC confirmed. Do you require a Balcony or Pool Access?"
        elif "ac" in text:
            st.session_state.booking_data['type'] = "AC"
            st.session_state.booking_step = 3
            return "AC configuration confirmed. Do you require a Balcony or Pool Access?"
        return "Please select: AC or Non-AC."

    elif step == 3:  # FEATURE
        if "pool" in text:
            st.session_state.booking_data['view'] = "Pool Access"
            price = "5000 Credits"
        else:
            st.session_state.booking_data['view'] = "Balcony"
            price = "3500 Credits"

        st.session_state.booking_step = 4
        return f"Configuration complete. Room type: {st.session_state.booking_data['type']} with {st.session_state.booking_data['view']}. Total: {price}. Do you authorize?"

    elif step == 4:  # CONFIRM
        if "yes" in text or "confirm" in text or "ok" in text:
            st.balloons()
            st.session_state.booking_step = 0  # Loop ends
            return "Authorization verified. Reservation uploaded to the mainframe. Goodbye."
        else:
            st.session_state.booking_step = 0
            return "Authorization denied. Resetting parameters."

    return response


# --- 6. UI LAYOUT ---

# Header
c1, c2 = st.columns([1, 15])
with c1:
    st.markdown("## 🧿")
with c2:
    st.markdown("## F.R.I.D.A.Y. \n *Simplotel Voice Interface*")

st.divider()

# Chat History Area
chat_placeholder = st.container(height=400)
with chat_placeholder:
    for msg in st.session_state.chat_history:
        with st.chat_message(msg['role']):
            st.write(msg['content'])

# --- INPUTS: VOICE & TEXT ---

# 1. Voice Input (The Orb)
c1, c2, c3 = st.columns([1, 1, 1])
with c2:
    st.write("**TAP ORB TO COMMUNICATE**")
    voice_text = speech_to_text(
        language='en',
        start_prompt="●",
        stop_prompt="■",
        just_once=True,
        key='orb_input'
    )

# 2. Text Input (Fallback)
text_text = st.chat_input("...or type command here")

# --- UNIFIED PROCESSING ---
user_input = None

if voice_text:
    user_input = voice_text
elif text_text:
    user_input = text_text

if user_input:
    # 1. Append User Message
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # 2. Logic Core
    bot_reply = core_logic(user_input)
    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

    # 3. Play Audio (Invisible Player)
    play_friday_voice(bot_reply)

    # 4. Refresh UI
    st.rerun()