import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import time
import base64
import pandas as pd

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="FRIDAY | By Faizan",
    page_icon="🧿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. DATABASE & STATE ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "history": [],
        "analytics": {"total": 0, "success": 0, "latency": []},
        "booking": {"guests": None, "type": None, "view": None, "confirmed": False}
    }
if 'system_ready' not in st.session_state:
    st.session_state.system_ready = False

# --- 3. LUXURY HOTEL CSS ---
st.markdown("""
<style>
    /* BACKGROUND IMAGE */
    .stApp {
        background: linear-gradient(to bottom, rgba(0,0,0,0.8), rgba(10,20,40,0.95)), 
                    url('https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        font-family: 'Segoe UI', sans-serif;
        color: white;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 15, 25, 0.9);
        border-right: 1px solid #00f2ff;
    }

    /* CHAT BUBBLES */
    .stChatMessage {
        background: rgba(0, 0, 0, 0.7);
        border: 1px solid rgba(0, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 15px;
    }
    div[data-testid="chatAvatarIcon-assistant"] { background-color: #00d4ff !important; }
    div[data-testid="chatAvatarIcon-user"] { background-color: #ff0055 !important; }

    /* METRICS */
    div[data-testid="metric-container"] {
        background: rgba(0, 242, 255, 0.05);
        border: 1px solid #00f2ff;
        border-radius: 5px;
        padding: 10px;
    }
    label[data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; }

    /* START BUTTON */
    .big-btn {
        border: 2px solid #00f2ff;
        color: #00f2ff;
        padding: 20px;
        text-align: center;
        border-radius: 10px;
        cursor: pointer;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- 4. AUDIO ENGINE ---
def play_friday_voice(text):
    """Generates audio and forces autoplay."""
    try:
        # Unique filename to prevent caching
        audio_file = f"voice_{int(time.time())}.mp3"

        # 'co.uk' accent for the Friday persona
        tts = gTTS(text=text, lang='en', tld='co.uk')
        tts.save(audio_file)

        with open(audio_file, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()

        # Hidden HTML5 Player
        md = f"""
            <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
        os.remove(audio_file)
    except Exception as e:
        st.error(f"Audio Error: {e}")


# --- 5. INTELLIGENCE (NLU) ---
def get_response(text):
    text = text.lower()
    bk = st.session_state.db['booking']

    # 1. RESET
    if any(x in text for x in ["reset", "cancel", "stop"]):
        st.session_state.db['booking'] = {"guests": None, "type": None, "view": None, "confirmed": False}
        return "System reset. I am ready for a new command.", False

    # 2. START
    if bk['guests'] is None and not any(x in text for x in ["book", "room"]):
        # If user says "Hi", nudge them to book
        if any(x in text for x in ["hi", "hello", "friday"]):
            return "Hello. I am online. Say 'Book a room' to begin.", False
        return "I am waiting. Please say 'Book a room'.", False

    if bk['guests'] is None:
        if "book" in text or "room" in text:
            return "Acknowledged. Initiating protocol. How many guests will be staying?", True
        # Extract Guests
        import re
        nums = re.findall(r'\d+', text)
        w2n = {"one": "1", "two": "2", "three": "3", "four": "4"}
        for k, v in w2n.items():
            if k in text: nums.append(v)

        if nums:
            st.session_state.db['booking']['guests'] = nums[0]
            return f"{nums[0]} guests registered. Do you require an AC or Non-AC suite?", True
        return "Numeric input required. How many guests?", False

    # 3. ROOM TYPE
    if bk['type'] is None:
        if "non" in text:
            st.session_state.db['booking']['type'] = "Non-AC"
            return "Non-AC selected. Would you like a Balcony or Pool Access?", True
        if "ac" in text:
            st.session_state.db['booking']['type'] = "AC"
            return "AC suite selected. Would you like a Balcony or Pool Access?", True
        return "Please specify: AC or Non-AC.", False

    # 4. VIEW
    if bk['view'] is None:
        if "pool" in text:
            st.session_state.db['booking']['view'] = "Pool Access"
            price = "5000"
        elif "balcony" in text:
            st.session_state.db['booking']['view'] = "Balcony"
            price = "3500"
        else:
            return "Option unavailable. Choose Balcony or Pool Access.", False

        return f"Configuration complete. Total is {price} credits. Do you authorize this transaction?", True

    # 5. CONFIRM
    if not bk['confirmed']:
        if any(x in text for x in ["yes", "confirm", "ok", "sure"]):
            st.session_state.db['booking']['confirmed'] = True
            st.balloons()
            return "Authorization Verified. Booking confirmed. Thank you for choosing us.", True
        return "Awaiting authorization. Say 'Yes' to confirm.", False

    return "Process complete. Say 'Reset' to start over.", False


# --- 6. UI LAYOUT ---

# SCENE 1: INITIALIZATION
if not st.session_state.system_ready:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown(
        "<h1 style='text-align: center; color: #00f2ff; text-shadow: 0 0 20px #00f2ff; font-size: 60px;'>FRIDAY AI</h1>",
        unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; letter-spacing: 2px;'>SYSTEM DEVELOPED BY FAIZAN</p>",
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("INITIALIZE SYSTEM", use_container_width=True):
            st.session_state.system_ready = True
            st.session_state.trigger_intro = True
            st.rerun()

# SCENE 2: MAIN INTERFACE
else:
    # SIDEBAR ANALYTICS
    with st.sidebar:
        st.title("📊 ANALYTICS")
        st.markdown("---")

        # Stats
        total = st.session_state.db['analytics']['total']
        succ = st.session_state.db['analytics']['success']

        c1, c2 = st.columns(2)
        c1.metric("Queries", total)
        c2.metric("Success", succ)

        # Chart
        st.write("**Latency (ms)**")
        if st.session_state.db['analytics']['latency']:
            st.line_chart(st.session_state.db['analytics']['latency'])

        st.divider()
        st.json(st.session_state.db['booking'])

        if st.button("REBOOT SYSTEM", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # MAIN AREA
    st.markdown("<h2 style='text-align: center; color: #00f2ff;'>SIMPLOTEL AI CONCIERGE</h2>", unsafe_allow_html=True)
    st.divider()

    # Chat History
    chat_box = st.container(height=400)
    with chat_box:
        for msg in st.session_state.db['history']:
            with st.chat_message(msg['role']):
                st.write(msg['content'])

    # INPUT AREA
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])

    with c1:
        text_input = st.chat_input("Type command here...")

    with c2:
        # START / STOP BUTTONS
        voice_text = speech_to_text(
            start_prompt="▶️ START LISTENING",
            stop_prompt="⏹️ STOP & SEND",
            language='en',
            just_once=False,
            key='voice_panel'
        )

    # --- PROCESSING ENGINE ---
    user_final = voice_text if voice_text else text_input

    # 1. TRIGGER INTRO (Once)
    if st.session_state.get('trigger_intro'):
        intro_text = "System Online. I am Friday, your AI Concierge, developed by Faizan. Please say 'Book a room' to begin."
        st.session_state.db['history'].append({"role": "assistant", "content": intro_text})
        play_friday_voice(intro_text)
        st.session_state.trigger_intro = False
        st.rerun()

    # 2. HANDLE USER INPUT
    if user_final:
        start_ts = time.time()

        # Log User
        st.session_state.db['history'].append({"role": "user", "content": user_final})

        # Get Response
        bot_reply, success_flag = get_response(user_final)

        # Log Bot
        st.session_state.db['history'].append({"role": "assistant", "content": bot_reply})

        # Analytics Update
        st.session_state.db['analytics']['total'] += 1
        if success_flag: st.session_state.db['analytics']['success'] += 1
        st.session_state.db['analytics']['latency'].append(round(time.time() - start_ts, 3))

        # SPEAK (Crucial Step)
        play_friday_voice(bot_reply)

        # Refresh
        st.rerun()