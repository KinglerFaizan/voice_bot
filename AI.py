import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import time
import base64
import pandas as pd
import datetime

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(
    page_title="FRIDAY | Enterprise AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. MOCK BACKEND / DATABASE (Session State) ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "history": [],
        "analytics": {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "response_times": []
        },
        "booking": {"guests": None, "type": None, "view": None, "confirmed": False}
    }

if 'system_ready' not in st.session_state:
    st.session_state.system_ready = False


# --- 3. ANALYTICS ENGINE ---
def update_analytics(start_time, success=True):
    end_time = time.time()
    latency = round(end_time - start_time, 2)

    st.session_state.db['analytics']['total_queries'] += 1
    st.session_state.db['analytics']['response_times'].append(latency)

    if success:
        st.session_state.db['analytics']['successful_queries'] += 1
    else:
        st.session_state.db['analytics']['failed_queries'] += 1


# --- 4. AUDIO ENGINE (FORCED AUTOPLAY) ---
def play_friday_voice(text):
    """Generates audio and injects a hidden HTML5 player to force sound."""
    try:
        # 1. Generate MP3
        filename = f"friday_{int(time.time())}.mp3"
        tts = gTTS(text=text, lang='en', tld='co.uk')  # British accent
        tts.save(filename)

        # 2. Read as Binary
        with open(filename, "rb") as f:
            data = f.read()

        # 3. Encode to Base64 for HTML embedding
        b64 = base64.b64encode(data).decode()

        # 4. Embed Hidden Player
        md = f"""
            <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

        # 5. Cleanup
        os.remove(filename)

    except Exception as e:
        st.error(f"TTS Error: {e}")


# --- 5. NATURAL LANGUAGE UNDERSTANDING (NLU) ---
def intent_recognition(text):
    text = text.lower()

    # Intent: Reset
    if any(x in text for x in ["reset", "cancel", "stop", "restart"]):
        return "reset"

    # Intent: Booking Init
    if any(x in text for x in ["book", "room", "reservation"]):
        return "book_room"

    # Intent: Guests (Entity Extraction)
    import re
    nums = re.findall(r'\d+', text)
    w2n = {"one": "1", "two": "2", "three": "3", "four": "4"}
    for k, v in w2n.items():
        if k in text: nums.append(v)
    if nums:
        return f"guests_{nums[0]}"

    # Intent: Room Type
    if "non" in text: return "type_non_ac"
    if "ac" in text: return "type_ac"

    # Intent: Features
    if "pool" in text: return "view_pool"
    if "balcony" in text: return "view_balcony"

    # Intent: Confirmation
    if any(x in text for x in ["yes", "ok", "confirm", "sure"]):
        return "confirm_yes"

    return "unknown"


# --- 6. RESPONSE GENERATION LOGIC ---
def generate_response(intent):
    step = 0
    booking = st.session_state.db['booking']

    # Determine current step based on missing data
    if booking['guests'] is None:
        step = 1
    elif booking['type'] is None:
        step = 2
    elif booking['view'] is None:
        step = 3
    elif not booking['confirmed']:
        step = 4

    # Logic Tree
    if intent == "reset":
        st.session_state.db['booking'] = {"guests": None, "type": None, "view": None, "confirmed": False}
        return "System reset. Say 'Book a room' to start over.", True

    if intent == "book_room":
        return "Acknowledged. Initiating protocol. How many guests will be staying?", True

    if step == 1 and "guests_" in intent:
        count = intent.split("_")[1]
        st.session_state.db['booking']['guests'] = count
        return f"{count} guests registered. Do you require an AC or Non-AC room?", True

    if step == 2:
        if intent == "type_ac":
            st.session_state.db['booking']['type'] = "AC"
            return "AC Room selected. Would you like a Balcony or Pool Access?", True
        elif intent == "type_non_ac":
            st.session_state.db['booking']['type'] = "Non-AC"
            return "Non-AC Room selected. Would you like a Balcony or Pool Access?", True

    if step == 3:
        if intent == "view_pool":
            st.session_state.db['booking']['view'] = "Pool Access"
            price = "5000"
        elif intent == "view_balcony":
            st.session_state.db['booking']['view'] = "Balcony"
            price = "3500"
        else:
            return "Please choose: Balcony or Pool Access.", False  # Failed intent

        return f"Configuration complete. Total price is {price}. Do you authorize this?", True

    if step == 4 and intent == "confirm_yes":
        st.session_state.db['booking']['confirmed'] = True
        st.balloons()
        return "Authorization Verified. Booking confirmed. Thank you for using Friday.", True

    return "I didn't understand that. Please repeat.", False


# --- 7. UI STYLING (Futuristic) ---
st.markdown("""
<style>
    .stApp {
        background: #0e1117;
        color: #00ffcc;
        font-family: 'Segoe UI', sans-serif;
    }
    /* Status Bar */
    .status-panel {
        background: rgba(0, 255, 204, 0.1);
        border: 1px solid #00ffcc;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    /* Chat Bubbles */
    .stChatMessage {
        background-color: #1a1d23;
        border: 1px solid #333;
    }
    /* Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #1a1d23;
        border-left: 4px solid #00ffcc;
        padding: 10px;
    }
    /* Start Button */
    .big-button {
        width: 100%; 
        height: 60px; 
        font-size: 24px;
        background-color: #00ffcc;
        color: black;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 8. MAIN APPLICATION LAYOUT ---

# SIDEBAR: ANALYTICS DASHBOARD
with st.sidebar:
    st.title("📊 ANALYTICS CORE")
    st.caption("Real-time Performance Monitoring")
    st.divider()

    # Metrics
    total = st.session_state.db['analytics']['total_queries']
    success = st.session_state.db['analytics']['successful_queries']
    error_rate = round(((total - success) / total * 100) if total > 0 else 0, 1)

    col1, col2 = st.columns(2)
    col1.metric("Total Queries", total)
    col2.metric("Error Rate", f"{error_rate}%")

    # Response Time Chart
    st.write("**Response Latency (ms)**")
    if st.session_state.db['analytics']['response_times']:
        st.line_chart(st.session_state.db['analytics']['response_times'])
    else:
        st.info("No data yet.")

    st.divider()
    st.write("**DATABASE STATUS**")
    st.json(st.session_state.db['booking'])

# MAIN SCREEN: SYSTEM INIT
if not st.session_state.system_ready:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #00ffcc;'>FRIDAY AI CONCIERGE</h1>", unsafe_allow_html=True)
    st.markdown("<div class='status-panel'>SYSTEM STANDBY. AUDIO PROTOCOLS REQUIRED.</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("INITIALIZE SYSTEM", use_container_width=True):
            st.session_state.system_ready = True
            st.session_state.trigger_intro = True
            st.rerun()

# MAIN SCREEN: ACTIVE INTERFACE
else:
    st.title("🧿 FRIDAY INTERFACE")
    st.markdown(f"**Instructions:** Click 'START' to speak. Click 'STOP' when done. Say **'Book a room'** to begin.")

    # Chat History Display
    chat_box = st.container(height=400)
    with chat_box:
        for msg in st.session_state.db['history']:
            with st.chat_message(msg['role']):
                st.write(msg['content'])

    st.divider()

    # --- INPUT AREA ---
    c1, c2 = st.columns([3, 1])

    with c1:
        # Text Fallback
        text_input = st.chat_input("Type command or use voice panel ->")

    with c2:
        # 🎙️ SPEECH RECOGNITION (START / STOP)
        # 'start_prompt' and 'stop_prompt' create the actual buttons you click
        voice_text = speech_to_text(
            start_prompt="▶️ START LISTENING",
            stop_prompt="⏹️ STOP & SEND",
            language='en',
            just_once=False,  # Allows toggling
            key='voice_input'
        )

    # --- PROCESSING ENGINE ---
    user_final = voice_text if voice_text else text_input

    # Intro Trigger
    if st.session_state.get('trigger_intro'):
        intro_msg = "System Online. I am Friday. Please say 'Book a room' to begin."
        st.session_state.db['history'].append({"role": "assistant", "content": intro_msg})
        play_friday_voice(intro_msg)
        st.session_state.trigger_intro = False
        st.rerun()

    # User Input Logic
    if user_final:
        # 1. Start Timer
        start_ts = time.time()

        # 2. Log User Input
        st.session_state.db['history'].append({"role": "user", "content": user_final})

        # 3. NLU & Response Gen
        intent = intent_recognition(user_final)
        bot_reply, is_success = generate_response(intent)

        # 4. Update Analytics
        update_analytics(start_ts, success=is_success)

        # 5. Log Bot Response
        st.session_state.db['history'].append({"role": "assistant", "content": bot_reply})

        # 6. Speak
        play_friday_voice(bot_reply)

        # 7. Refresh
        st.rerun()