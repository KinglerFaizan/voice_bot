import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import time
import base64
import pandas as pd
import datetime

# --- 1. CORE CONFIGURATION ---
st.set_page_config(
    page_title="F.R.I.D.A.Y. | Protocol Active",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. MEMORY BANKS (Session State) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "history": [],
        "analytics": {
            "queries": 0,
            "success": 0,
            "latency": []
        },
        "booking": {
            "dates": None,
            "guests": None,
            "type": None,
            "view": None,
            "name": None,
            "confirmed": False
        }
    }
if 'system_ready' not in st.session_state:
    st.session_state.system_ready = False
if 'audio_queue' not in st.session_state:
    st.session_state.audio_queue = None

# --- 3. INVENTORY DATA MATRIX ---
ROOM_DATA = pd.DataFrame({
    "CLASS": ["MARK 1 (Standard)", "MARK 5 (Deluxe)", "HULKBUSTER (Suite)"],
    "VIEW": ["City", "Garden", "Ocean"],
    "COST": ["$200", "$500", "$1500"],
    "STATUS": ["ONLINE", "ONLINE", "LIMITED"]
})

# --- 4. IRONMAN HUD CSS ---
st.markdown("""
<style>
    /* IMPORT SCI-FI FONT */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500&display=swap');

    /* MAIN INTERFACE BACKGROUND */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(10,20,30,0.9)), 
                    url('https://wallpapers.com/images/hd/iron-man-jarvis-hud-interface-1920-x-1080-wallpaper-j03j2j2j2j2j2j2j.jpg');
        background-size: cover;
        background-attachment: fixed;
        font-family: 'Rajdhani', sans-serif;
        color: #00f3ff;
    }

    /* SIDEBAR (HOLOGRAPHIC PANEL) */
    [data-testid="stSidebar"] {
        background-color: rgba(5, 10, 15, 0.9);
        border-right: 2px solid #00f3ff;
        box-shadow: 5px 0 15px rgba(0, 243, 255, 0.2);
    }

    /* METRIC CARDS */
    div[data-testid="metric-container"] {
        background: rgba(0, 243, 255, 0.05);
        border: 1px solid #00f3ff;
        border-radius: 5px;
        padding: 10px;
        transition: 0.3s;
    }
    div[data-testid="metric-container"]:hover {
        box-shadow: 0 0 15px #00f3ff inset;
    }
    label[data-testid="stMetricLabel"] { color: #00f3ff !important; font-family: 'Orbitron', sans-serif; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-family: 'Orbitron', sans-serif; }

    /* CHAT BUBBLES */
    .stChatMessage {
        background: rgba(0, 10, 20, 0.8);
        border: 1px solid rgba(0, 243, 255, 0.3);
        border-radius: 0px 15px 15px 15px;
        backdrop-filter: blur(5px);
    }
    div[data-testid="chatAvatarIcon-assistant"] { background-color: #00f3ff !important; color: black !important; }
    div[data-testid="chatAvatarIcon-user"] { background-color: #ff0055 !important; }

    /* ARC REACTOR BUTTON */
    .start-btn {
        font-family: 'Orbitron', sans-serif;
        font-size: 24px;
        padding: 20px;
        color: #00f3ff;
        background: radial-gradient(circle, rgba(0,243,255,0.2) 0%, rgba(0,0,0,0.8) 100%);
        border: 2px solid #00f3ff;
        border-radius: 50%;
        width: 200px;
        height: 200px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 30px #00f3ff;
        animation: pulse 2s infinite;
        cursor: pointer;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 10px #00f3ff; }
        50% { box-shadow: 0 0 40px #00f3ff, 0 0 20px #00f3ff inset; }
        100% { box-shadow: 0 0 10px #00f3ff; }
    }

    /* HIDE JUNK */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- 5. FRIDAY VOICE PROTOCOL ---
def play_friday_voice(text):
    """Generates audio and creates a hidden HTML player to force browser playback."""
    try:
        filename = f"friday_{int(time.time())}.mp3"
        # British accent ('co.uk') mimics J.A.R.V.I.S / F.R.I.D.A.Y tone
        tts = gTTS(text=text, lang='en', tld='co.uk')
        tts.save(filename)

        with open(filename, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()

        md = f"""
            <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
        os.remove(filename)
    except Exception as e:
        st.error(f"VOICE MODULE FAILURE: {e}")


# --- 6. CONVERSATION LOGIC ENGINE ---
def process_booking_flow(text):
    text = text.lower()
    bk = st.session_state.db['booking']

    # --- GLOBAL RESET ---
    if any(x in text for x in ["reset", "cancel", "abort", "stop"]):
        st.session_state.db['booking'] = {k: None for k in bk}
        st.session_state.db['booking']['confirmed'] = False
        return "System protocols reset. Ready for new assignment.", False

    # STEP 0: INITIALIZE
    if bk['dates'] is None and not any(x in text for x in ["book", "room"]):
        if any(x in text for x in ["hi", "hello", "friday", "jarvis"]):
            return "Greetings. I am online. State your reservation requirements.", False
        return "I am waiting for a command. Say 'Book a room'.", False

    # STEP 1: DATES
    if bk['dates'] is None:
        if "book" in text or "room" in text:
            return "Processing request. Accessing calendar. What dates do you require?", True

        # Save Dates
        st.session_state.db['booking']['dates'] = text
        return f"Dates locked for {text}. How many guests will be accompanying you?", True

    # STEP 2: GUESTS
    if bk['guests'] is None:
        import re
        nums = re.findall(r'\d+', text)
        w2n = {"one": "1", "two": "2", "three": "3", "four": "4"}
        for k, v in w2n.items():
            if k in text: nums.append(v)

        if nums:
            st.session_state.db['booking']['guests'] = nums[0]