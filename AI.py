import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import time
import base64
import pandas as pd

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="FRIDAY | System Active",
    page_icon="🧿",
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
if 'system_ready' not in st.session_state:
    st.session_state.system_ready = False
if 'intro_played' not in st.session_state:
    st.session_state.intro_played = False

# --- 3. DATA FOR DASHBOARD ---
ROOM_DATA = pd.DataFrame({
    "CLASS": ["Standard", "Deluxe", "Presidential"],
    "VIEW": ["City", "Garden", "Ocean"],
    "PRICE": ["$200", "$500", "$1500"],
    "STATUS": ["OPEN", "OPEN", "WAITLIST"]
})

# --- 4. HIGH-TECH CSS ---
st.markdown("""
<style>
    /* MAIN BG */
    .stApp {
        background: linear-gradient(to bottom, #020205, #0a1020), 
                    url('https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-blend-mode: overlay;
        font-family: 'Segoe UI', sans-serif;
        color: #e0e0e0;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: rgba(5, 10, 20, 0.95);
        border-right: 2px solid #00f3ff;
    }

    /* CHAT MESSAGES */
    .stChatMessage {
        background: rgba(0, 243, 255, 0.05);
        border: 1px solid rgba(0, 243, 255, 0.2);
        border-radius: 12px;
        backdrop-filter: blur(5px);
    }
    div[data-testid="chatAvatarIcon-assistant"] { background-color: #00f3ff !important; color: #000 !important; }
    div[data-testid="chatAvatarIcon-user"] { background-color: #ff0055 !important; }

    /* SINGLE TOGGLE BUTTON STYLING */
    /* We style the Start and Stop states to look distinct but cool */
    button[kind="secondary"] {
        background: transparent;
        border: 2px solid #00f3ff;
        color: #00f3ff;
        border-radius: 50px;
        transition: 0.3s;
        font-weight: bold;
    }
    button[kind="secondary"]:hover {
        box-shadow: 0 0 15px #00f3ff;
        background: rgba(0, 243, 255, 0.1);
    }
    /* This targets the active recording state if library supports dynamic classes, 
       otherwise handled by prompt text */

    /* DATAFRAME */
    [data-testid="stDataFrame"] {
        border: 1px solid #00f3ff;
    }

    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- 5. AUDIO ENGINE ---
def play_friday_voice(text):
    """Generates audio and forces it to play."""
    try:
        filename = f"audio_{int(time.time())}.mp3"
        # 'co.uk' British accent for Friday persona
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
        st.error(f"Audio Error: {e}")


# --- 6. EXTENDED CONVERSATION LOGIC ---
def get_response(text):
    text = text.lower()
    bk = st.session_state.db['booking']

    # GLOBAL RESET
    if any(x in text for x in ["reset", "cancel", "stop"]):
        st.session_state.db['booking'] = {k: None for k in bk}
        st.session_state.db['booking']['confirmed'] = False
        return "System reset. All protocols cleared. Ready for new command.", False

    # 1. START (If nothing set)
    if bk['dates'] is None and not any(x in text for x in ["book", "room"]):
        if any(x in text for x in ["hi", "hello", "friday"]):
            return "Hello. I am online. State your reservation request to begin.", False
        return "I am waiting. Please say 'Book a room'.", False

    # 2. DATES (First Step)
    if bk['dates'] is None:
        if "book" in text or "room" in text:
            return "Acknowledged. Initiating reservation protocol. For which dates would you like to book?", True
        # Capture anything as date for now (simple logic)
        st.session_state.db['booking']['dates'] = text
        return f"Dates set for {text}. How many guests will be accompanying you?", True

    # 3. GUESTS
    if bk['guests'] is None:
        import re
        nums = re.findall(r'\d+', text)
        w2n = {"one": "1", "two": "2", "three": "3", "four": "4"}
        for k, v in w2n.items():
            if k in text: nums.append(v)

        if nums:
            st.session_state.db['booking']['guests'] = nums[0]
            return f"{nums[0]} guests registered. Please select your room class: Standard, Deluxe, or Presidential?", True
        return "Numeric input required. How many guests?", False

    # 4. ROOM TYPE
    if bk['type'] is None:
        if "standard" in text:
            st.session_state.db['booking']['type'] = "Standard"
            return "Standard Class selected. Do you prefer a City view?", True
        if "deluxe" in text:
            st.session_state.db['booking']['type'] = "Deluxe"
            return "Deluxe Class selected. Do you prefer a Garden view?", True
        if "presidential" in text or "suite" in text:
            st.session_state.db['booking']['type'] = "Presidential"
            return "Presidential Suite selected. Do you prefer an Ocean view?", True
        return "Please choose a class: Standard, Deluxe, or Presidential.", False

    # 5. VIEW
    if bk['view'] is None:
        if any(x in text for x in ["city", "garden", "ocean", "sea"]):
            st.session_state.db['booking']['view'] = "Selected View"
            return "View preference logged. May I have the name for the reservation?", True
        if "yes" in text:  # Default answer
            st.session_state.db['booking']['view'] = "Standard View"
            return "View confirmed. What is the name for the booking?", True
        return "Please confirm your view preference.", False

    # 6. NAME
    if bk['name'] is None:
        st.session_state.db['booking']['name'] = text.title()
        return f"Thank you, {text.title()}. Reviewing data: {bk['type']} room for {bk['guests']} guests on {bk['dates']}. Do you authorize this transaction?", True

    # 7. CONFIRM
    if not bk['confirmed']:
        if any(x in text for x in ["yes", "confirm", "ok", "sure"]):
            st.session_state.db['booking']['confirmed'] = True
            st.balloons()
            return "Authorization Verified. Reservation uploaded to Simplotel mainframe. Goodbye.", True
        return "Awaiting authorization. Say 'Yes' to confirm.", False

    return "Process complete. Say 'Reset' to start over.", False


# --- 7. UI LAYOUT ---

# SCENE 1: BOOT SCREEN (Required for Voice Permission)
if not st.session_state.system_ready:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown(
            "<h1 style='text-align: center; color: #00f3ff; text-shadow: 0 0 20px #00f3ff; font-size: 50px;'>FRIDAY AI</h1>",
            unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; letter-spacing: 4px;'>SYSTEM DEVELOPED BY FAIZAN</p>",
                    unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # CLICKING THIS ENABLES THE VOICE INTRO
        if st.button("BOOT SYSTEM PROTOCOLS", use_container_width=True):
            st.session_state.system_ready = True
            st.session_state.intro_needed = True  # Flag to play intro next refresh
            st.rerun()

# SCENE 2: MAIN DASHBOARD
else:
    # SIDEBAR: INVENTORY & STATUS
    with st.sidebar:
        st.title("📊 LIVE INVENTORY")
        st.markdown("---")
        st.dataframe(ROOM_DATA, hide_index=True)

        st.markdown("---")
        st.write("### LIVE SESSION DATA")
        # Dynamic JSON display of the booking dictionary
        st.json(st.session_state.db['booking'])

        st.markdown("---")
        if st.button("EMERGENCY RESET", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # MAIN CHAT AREA
    st.markdown("<h2 style='text-align: center; color: #00f3ff;'>SIMPLOTEL COMMAND CENTER</h2>", unsafe_allow_html=True)
    st.divider()

    # Message History
    chat_box = st.container(height=400)
    with chat_box:
        for msg in st.session_state.db['history']:
            with st.chat_message(msg['role']):
                st.write(msg['content'])

    # INPUTS
    c1, c2 = st.columns([3, 1])

    with c1:
        text_input = st.chat_input("Manual Override (Type Here)...")

    with c2:
        # SINGLE TOGGLE BUTTON
        # When idle: Shows "Start Recording"
        # When recording: Shows "Stop & Send"
        voice_text = speech_to_text(
            start_prompt="🔴 START RECORDING",
            stop_prompt="✅ STOP & SEND",
            language='en',
            just_once=False,
            key='voice_control'
        )

    # LOGIC
    user_final = voice_text if voice_text else text_input

    # 1. HANDLE INTRO (Runs Once immediately after Boot)
    if st.session_state.get('intro_needed'):
        intro_text = "System Online. I am Friday, your AI Concierge, developed by Faizan. I am ready to assist with your booking."
        st.session_state.db['history'].append({"role": "assistant", "content": intro_text})
        play_friday_voice(intro_text)
        st.session_state.intro_needed = False
        st.rerun()

    # 2. HANDLE USER INTERACTION
    if user_final:
        # Log User
        st.session_state.db['history'].append({"role": "user", "content": user_final})

        # Get Response
        bot_reply, success_flag = get_response(user_final)

        # Log Bot
        st.session_state.db['history'].append({"role": "assistant", "content": bot_reply})

        # Speak
        play_friday_voice(bot_reply)

        # Refresh (small delay to ensure audio generates)
        time.sleep(0.2)
        st.rerun()