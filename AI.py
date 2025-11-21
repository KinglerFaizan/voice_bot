import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import time
import base64
import pandas as pd

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="FRIDAY | Simplotel",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. STATE MANAGEMENT ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "history": [],
        "booking": {
            "dates": None,
            "guests": None,
            "type": None,
            "view": None,
            "name": None,
            "confirmed": False
        }
    }
if 'booking_step' not in st.session_state:
    st.session_state.booking_step = 0
if 'system_ready' not in st.session_state:
    st.session_state.system_ready = False
if 'trigger_audio' not in st.session_state:
    st.session_state.trigger_audio = None

# --- 3. DASHBOARD DATA ---
ROOM_DATA = pd.DataFrame({
    "CLASS": ["Standard", "Deluxe", "Presidential"],
    "VIEW": ["City", "Garden", "Ocean"],
    "PRICE": ["$200", "$500", "$1500"],
    "AVAILABILITY": ["High", "Medium", "Low"]
})

# --- 4. DARK LUXURY CSS ---
st.markdown("""
<style>
    /* MAIN BACKGROUND - Dark Hotel Image with Overlay */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)), 
                    url('https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        font-family: 'Segoe UI', sans-serif;
        color: #e0e0e0;
    }

    /* SIDEBAR - Glassmorphism */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.85);
        border-right: 2px solid #00f3ff;
        backdrop-filter: blur(10px);
    }

    /* CHAT MESSAGES */
    .stChatMessage {
        background: rgba(0, 20, 40, 0.8);
        border: 1px solid rgba(0, 243, 255, 0.2);
        backdrop-filter: blur(5px);
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    div[data-testid="chatAvatarIcon-assistant"] { background-color: #00f3ff !important; color: #000 !important; }
    div[data-testid="chatAvatarIcon-user"] { background-color: #ff0055 !important; }

    /* NEON TEXT HIGHLIGHTS */
    h1, h2, h3 {
        color: #00f3ff !important;
        text-shadow: 0 0 15px rgba(0, 243, 255, 0.5);
    }

    /* START BUTTON */
    .big-btn {
        font-size: 24px;
        font-weight: bold;
        color: #00f3ff;
        border: 2px solid #00f3ff;
        background: rgba(0,0,0,0.8);
        padding: 20px;
        border-radius: 10px;
        cursor: pointer;
        transition: 0.3s;
    }

    /* DATAFRAME */
    [data-testid="stDataFrame"] { border: 1px solid #00f3ff; }

    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- 5. AUDIO ENGINE ---
def play_audio_html(text):
    """Generates audio and returns the HTML player code."""
    try:
        filename = f"audio_{int(time.time())}.mp3"
        tts = gTTS(text=text, lang='en', tld='co.uk')
        tts.save(filename)

        with open(filename, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()

        # Cleanup immediately
        os.remove(filename)

        return f"""
            <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
    except Exception:
        return ""


# --- 6. LOGIC CORE ---
def process_logic(text):
    text = text.lower()
    step = st.session_state.booking_step
    bk = st.session_state.db['booking']

    # RESET
    if any(x in text for x in ["reset", "cancel", "stop"]):
        st.session_state.booking_step = 0
        st.session_state.db['booking'] = {k: None for k in bk}
        return "System reset. I am ready for a new booking."

    # STEP 0: START -> Ask for DATES
    if step == 0:
        st.session_state.booking_step = 1
        return "System Online. I am Friday. Let's book your stay. What dates are you looking for?"

    # STEP 1: DATES -> Ask for GUESTS
    elif step == 1:
        st.session_state.db['booking']['dates'] = text
        st.session_state.booking_step = 2
        return f"Dates set for {text}. How many guests will be staying?"

    # STEP 2: GUESTS -> Ask for TYPE
    elif step == 2:
        import re
        nums = re.findall(r'\d+', text)
        w2n = {"one": "1", "two": "2", "three": "3", "four": "4"}
        for k, v in w2n.items():
            if k in text: nums.append(v)

        if nums:
            st.session_state.db['booking']['guests'] = nums[0]
            st.session_state.booking_step = 3
            return f"{nums[0]} guests confirmed. Please select a Room Class: Standard, Deluxe, or Presidential?"
        else:
            return "I need a number for the guests. Please repeat."

    # STEP 3: TYPE -> Ask for VIEW
    elif step == 3:
        if "standard" in text:
            st.session_state.db['booking']['type'] = "Standard"
            st.session_state.booking_step = 4
            return "Standard Class. Do you prefer a City View?"
        elif "deluxe" in text:
            st.session_state.db['booking']['type'] = "Deluxe"
            st.session_state.booking_step = 4
            return "Deluxe Class. Do you prefer a Garden View?"
        elif "presidential" in text:
            st.session_state.db['booking']['type'] = "Presidential"
            st.session_state.booking_step = 4
            return "Presidential Suite. Do you prefer an Ocean View?"
        else:
            return "Please choose: Standard, Deluxe, or Presidential."

    # STEP 4: VIEW -> Ask for NAME
    elif step == 4:
        view_sel = "Standard View"
        if "city" in text:
            view_sel = "City View"
        elif "garden" in text:
            view_sel = "Garden View"
        elif "ocean" in text or "sea" in text:
            view_sel = "Ocean View"

        st.session_state.db['booking']['view'] = view_sel
        st.session_state.booking_step = 5
        return f"{view_sel} confirmed. Finally, under what name should I make this booking?"

    # STEP 5: NAME -> Ask for CONFIRM
    elif step == 5:
        st.session_state.db['booking']['name'] = text.title()
        st.session_state.booking_step = 6
        b = st.session_state.db['booking']
        return f"Reservation for {b['name']}: {b['type']} room, {b['view']}, {b['guests']} guests, on {b['dates']}. Do you authorize?"

    # STEP 6: CONFIRM -> Finish
    elif step == 6:
        if any(x in text for x in ["yes", "confirm", "ok", "sure"]):
            st.balloons()
            st.session_state.booking_step = 0
            return "Authorization Verified. Reservation uploaded to Simplotel mainframe. Goodbye."
        else:
            st.session_state.booking_step = 0
            return "Booking cancelled. Resetting system."

    return "I didn't catch that."


# --- 7. UI LAYOUT ---

# === SCENE 1: BOOT SCREEN ===
if not st.session_state.system_ready:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>FRIDAY AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #e0e0e0;'>SYSTEM INITIALIZATION REQUIRED</p>",
                    unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("BOOT SYSTEM PROTOCOLS", use_container_width=True):
            st.session_state.system_ready = True
            # Intro
            intro = "System Online. I am Friday, developed by Faizan. Please say 'Book a room' to begin."
            st.session_state.db['history'].append({"role": "assistant", "content": intro})
            st.session_state.trigger_audio = intro
            st.rerun()

# === SCENE 2: MAIN DASHBOARD ===
else:
    # SIDEBAR
    with st.sidebar:
        st.title("📊 LIVE INVENTORY")
        st.markdown("---")
        st.dataframe(ROOM_DATA, hide_index=True)

        st.markdown("---")
        st.write("### SESSION DATA")
        st.json(st.session_state.db['booking'])

        if st.button("EMERGENCY RESET", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # MAIN CHAT
    st.markdown("<h2 style='text-align: center;'>SIMPLOTEL COMMAND CENTER</h2>", unsafe_allow_html=True)
    st.divider()

    chat_box = st.container(height=400)
    with chat_box:
        for msg in st.session_state.db['history']:
            with st.chat_message(msg['role']):
                st.write(msg['content'])

    # AUDIO PLAYER (Invisible)
    if st.session_state.trigger_audio:
        html_audio = play_audio_html(st.session_state.trigger_audio)
        st.markdown(html_audio, unsafe_allow_html=True)
        st.session_state.trigger_audio = None

    # INPUTS
    c1, c2 = st.columns([3, 1])
    with c1:
        text_input = st.chat_input("Type Command...")
    with c2:
        # VOICE BUTTON
        voice_text = speech_to_text(
            start_prompt="🔴 REC",
            stop_prompt="✅ SEND",
            language='en',
            just_once=False,
            key='voice_rec'
        )

    # HANDLING INPUT
    user_final = voice_text if voice_text else text_input

    if user_final:
        st.session_state.db['history'].append({"role": "user", "content": user_final})
        bot_reply = process_logic(user_final)
        st.session_state.db['history'].append({"role": "assistant", "content": bot_reply})
        st.session_state.trigger_audio = bot_reply
        st.rerun()