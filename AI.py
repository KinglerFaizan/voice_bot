import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import time
import base64
import pandas as pd

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(
    page_title="FRIDAY | PROTOCOL V.8",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "## FRIDAY AI CONCIERGE\nSystem Developed by Faizan."
    }
)

# --- 2. MEMORY BANKS ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "history": [],
        "booking": {
            "guests": None,
            "type": None,
            "confirmed": False
        }
    }
# Steps: 0=Init, 1=Guests, 2=Type, 3=Confirm, 4=ExitChoice
if 'booking_step' not in st.session_state:
    st.session_state.booking_step = 0
if 'system_ready' not in st.session_state:
    st.session_state.system_ready = False
if 'audio_buffer' not in st.session_state:
    st.session_state.audio_buffer = None

# --- 3. INVENTORY DATA ---
ROOM_DATA = pd.DataFrame({
    "SUITE CLASS": ["MARK III (Standard)", "MARK V (Deluxe)", "HULKBUSTER (Pres.)"],
    "CREDITS": ["200", "500", "1500"],
    "STATUS": ["ONLINE", "ONLINE", "RESTRICTED"]
})

# --- 4. STARK INDUSTRIES CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&display=swap');

    /* MAIN BACKGROUND */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(10,20,30,0.9)), 
                    url('https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
        font-family: 'Orbitron', sans-serif;
        color: #00f3ff;
    }

    /* INSTRUCTION BOX */
    .instruction-box {
        background: rgba(0, 10, 20, 0.95);
        border: 2px solid #00f3ff;
        border-radius: 10px;
        padding: 20px;
        text-align: left;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
    }
    .instruction-title {
        color: #00f3ff;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
        text-transform: uppercase;
        text-align: center;
        text-shadow: 0 0 10px #00f3ff;
    }
    .instruction-text {
        color: #e0e0e0;
        font-family: 'Segoe UI', sans-serif;
        font-size: 15px;
        margin: 8px 0;
        line-height: 1.5;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: rgba(5, 10, 15, 0.95);
        border-right: 2px solid #00f3ff;
        box-shadow: 10px 0 30px rgba(0, 243, 255, 0.1);
    }

    /* CHAT BUBBLES */
    .stChatMessage {
        background: rgba(0, 20, 40, 0.85);
        border: 1px solid rgba(0, 243, 255, 0.3);
        border-radius: 0px 20px 20px 20px;
        backdrop-filter: blur(5px);
        color: white;
    }
    div[data-testid="chatAvatarIcon-assistant"] { background-color: #00f3ff !important; color: black !important; }
    div[data-testid="chatAvatarIcon-user"] { background-color: #ff0055 !important; }

    /* ARC REACTOR BUTTON */
    div.stButton > button:first-child {
        background: radial-gradient(circle, #e6ffff 0%, #00f3ff 30%, #000000 70%);
        border: 2px solid #00f3ff;
        color: transparent;
        border-radius: 50%;
        height: 140px;
        width: 140px;
        box-shadow: 0 0 30px #00f3ff, 0 0 60px #00f3ff inset;
        margin: 0 auto;
        display: block;
        animation: reactor-pulse 3s infinite;
        transition: 0.2s;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.05);
        box-shadow: 0 0 50px #00f3ff, 0 0 100px #00f3ff inset;
    }
    div.stButton > button:first-child:active, div.stButton > button:first-child:focus {
        border-color: #ff0055;
        box-shadow: 0 0 50px #ff0055, 0 0 100px #ff0055 inset;
        background: radial-gradient(circle, #ffcccc 0%, #ff0055 30%, #000000 70%);
    }

    @keyframes reactor-pulse {
        0% { box-shadow: 0 0 10px #00f3ff; }
        50% { box-shadow: 0 0 40px #00f3ff, 0 0 20px #00f3ff inset; }
        100% { box-shadow: 0 0 10px #00f3ff; }
    }

    /* BOOT BUTTON */
    .boot-btn {
        font-size: 24px;
        color: #00f3ff;
        border: 2px solid #00f3ff;
        background: rgba(0,0,0,0.8);
        padding: 20px;
        cursor: pointer;
    }

    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- 5. AUDIO ENGINE ---
def generate_audio_html(text):
    """Generates audio and returns the HTML player code."""
    try:
        filename = f"jarvis_{int(time.time())}.mp3"
        tts = gTTS(text=text, lang='en', tld='co.uk')
        tts.save(filename)

        with open(filename, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()

        os.remove(filename)

        return f"""
            <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
    except Exception:
        return ""


# --- 6. LOGIC CORE (2 QUESTIONS + EXIT) ---
def process_logic(text):
    text = text.lower()
    step = st.session_state.booking_step
    bk = st.session_state.db['booking']

    # RESET
    if any(x in text for x in ["reset", "cancel", "stop"]):
        st.session_state.booking_step = 0
        st.session_state.db['booking'] = {k: None for k in bk}
        return "System reset. Ready for new booking."

    # STEP 0: INITIALIZE -> Ask Q1 (GUESTS)
    if step == 0:
        st.session_state.booking_step = 1
        return "System Online. I am Friday. Question 1: How many guests will be staying?"

    # STEP 1: GUESTS -> Ask Q2 (TYPE)
    elif step == 1:
        import re
        nums = re.findall(r'\d+', text)
        w2n = {"one": "1", "two": "2", "three": "3", "four": "4"}
        for k, v in w2n.items():
            if k in text: nums.append(v)

        if nums:
            st.session_state.db['booking']['guests'] = nums[0]
            st.session_state.booking_step = 2
            return f"{nums[0]} guests confirmed. Question 2: Would you like Standard, Deluxe, or Presidential Class?"
        return "Numerical input required. How many guests?"

    # STEP 2: TYPE -> Ask CONFIRM
    elif step == 2:
        if "standard" in text:
            st.session_state.db['booking']['type'] = "Standard"
        elif "deluxe" in text:
            st.session_state.db['booking']['type'] = "Deluxe"
        elif "presidential" in text:
            st.session_state.db['booking']['type'] = "Presidential"
        else:
            return "Please choose: Standard, Deluxe, or Presidential."

        st.session_state.booking_step = 3
        return f"{st.session_state.db['booking']['type']} room selected for {st.session_state.db['booking']['guests']} guests. Do you authorize this transaction?"

    # STEP 3: CONFIRM -> Ask EXIT
    elif step == 3:
        if any(x in text for x in ["yes", "confirm", "ok", "sure", "authorize"]):
            st.balloons()
            st.session_state.db['booking']['confirmed'] = True
            st.session_state.booking_step = 4  # Move to Exit Phase
            return "Authorization Verified. Booking Confirmed. Would you like to Exit System or Start New?"

        st.session_state.booking_step = 0
        return "Authorization Denied. Resetting protocols."

    # STEP 4: EXIT PHASE
    elif step == 4:
        if "exit" in text or "close" in text or "bye" in text:
            st.session_state.system_ready = False  # Shut down UI
            st.rerun()
            return "Shutting down."
        elif "start" in text or "new" in text:
            st.session_state.booking_step = 0
            st.session_state.db['booking'] = {k: None for k in bk}
            return "Reloading protocols. Ready for new booking."

        return "Please say 'Exit' to close or 'Start New' to restart."

    return "Input Unrecognized. Please repeat."


# --- 7. UI LAYOUT ---

# SCENE 1: BOOT SEQUENCE (Start Screen)
if not st.session_state.system_ready:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; font-size: 70px; text-shadow: 0 0 30px #00f3ff;'>F.R.I.D.A.Y.</h1>",
                    unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; letter-spacing: 8px; color: white;'>SIMPLOTEL AI CORE</p>",
                    unsafe_allow_html=True)

        # --- INSTRUCTIONS ADDED HERE ---
        st.markdown("""
        <div class="instruction-box">
            <div class="instruction-title">⚠️ MISSION PROTOCOLS</div>
            <p class="instruction-text">1. <b>BOOT:</b> Click <b>'INITIATE SYSTEM BOOT'</b> below to enable audio.</p>
            <p class="instruction-text">2. <b>START:</b> Click the <b>'🔴 CLICK TO RECORD'</b> button to speak.</p>
            <p class="instruction-text">3. <b>SEND:</b> Click <b>'✅ CLICK TO SEND'</b> (same button) to process.</p>
            <p class="instruction-text">4. <b>LISTEN:</b> Wait for Friday's audio response.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("INITIATE SYSTEM BOOT", use_container_width=True):
            st.session_state.system_ready = True
            # Trigger Intro Voice
            intro = "System Online. I am Friday, developed by Faizan. Question 1: How many guests will be staying?"
            st.session_state.db['history'].append({"role": "assistant", "content": intro})
            st.session_state.audio_buffer = intro
            st.session_state.booking_step = 1  # Go straight to listening for guests
            st.rerun()

# SCENE 2: COMMAND CENTER (Main App)
else:
    # --- SIDEBAR HUD ---
    with st.sidebar:
        st.title("📊 STATUS MONITOR")
        st.markdown("---")

        # Metrics
        st.metric("GUESTS", st.session_state.db['booking']['guests'])
        st.metric("SUITE", st.session_state.db['booking']['type'])

        st.markdown("---")
        st.markdown("### INVENTORY MATRIX")
        st.dataframe(ROOM_DATA, hide_index=True)

        if st.button("EMERGENCY REBOOT", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # --- MAIN HUD ---
    st.markdown("<h2 style='text-align: center; letter-spacing: 4px;'>COMMAND INTERFACE</h2>", unsafe_allow_html=True)
    st.divider()

    # Chat
    chat_box = st.container(height=400)
    with chat_box:
        for msg in st.session_state.db['history']:
            with st.chat_message(msg['role']):
                st.write(msg['content'])

    # AUDIO INJECTION (Hidden)
    if st.session_state.audio_buffer:
        html_audio = generate_audio_html(st.session_state.audio_buffer)
        st.markdown(html_audio, unsafe_allow_html=True)
        st.session_state.audio_buffer = None

    # --- CONTROLS ---
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])

    with c1:
        # Optional Text Input
        text_input = st.chat_input("MANUAL OVERRIDE...")

    with c2:
        # ARC REACTOR BUTTON (TOGGLE)
        voice_text = speech_to_text(
            start_prompt="🔴 CLICK TO RECORD AND TALK",
            stop_prompt="✅ CLICK TO SEND",
            language='en',
            just_once=False,
            key='arc_reactor'
        )

    # PROCESS INPUT
    user_final = voice_text if voice_text else text_input

    if user_final:
        st.session_state.db['history'].append({"role": "user", "content": user_final})
        bot_reply = process_logic(user_final)
        st.session_state.db['history'].append({"role": "assistant", "content": bot_reply})
        st.session_state.audio_buffer = bot_reply
        st.rerun()