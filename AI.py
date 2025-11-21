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
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. STATE MANAGEMENT ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "history": [],
        "booking": {"guests": None, "type": None, "view": None, "confirmed": False}
    }
if 'system_ready' not in st.session_state:
    st.session_state.system_ready = False
if 'intro_played' not in st.session_state:
    st.session_state.intro_played = False

# --- 3. AVAILABLE ROOMS DATA (For Dashboard) ---
ROOM_DATA = pd.DataFrame({
    "TYPE": ["Standard", "Deluxe", "Presidential"],
    "VIEW": ["City", "Garden", "Sea/Ocean"],
    "PRICE": ["$200", "$500", "$1500"],
    "STATUS": ["AVAILABLE", "AVAILABLE", "LIMITED"]
})

# --- 4. HIGH-TECH CSS ---
st.markdown("""
<style>
    /* MAIN BG */
    .stApp {
        background: linear-gradient(to bottom, #000000, #0a0f1e);
        color: #00f3ff;
        font-family: 'Courier New', Courier, monospace;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 2px solid #00f3ff;
    }

    /* DATAFRAME STYLING */
    [data-testid="stDataFrame"] {
        border: 1px solid #00f3ff;
        border-radius: 5px;
    }

    /* CHAT MESSAGES */
    .stChatMessage {
        background: rgba(0, 243, 255, 0.05);
        border: 1px solid rgba(0, 243, 255, 0.3);
        border-radius: 0px 15px 15px 15px;
        font-family: sans-serif;
    }
    div[data-testid="chatAvatarIcon-assistant"] { background-color: #00f3ff !important; color: black !important; }
    div[data-testid="chatAvatarIcon-user"] { background-color: #ff0055 !important; }

    /* NEON BUTTONS */
    .big-btn {
        width: 100%;
        padding: 15px;
        background: transparent;
        border: 2px solid #00f3ff;
        color: #00f3ff;
        font-size: 20px;
        text-transform: uppercase;
        letter-spacing: 3px;
        cursor: pointer;
        transition: 0.3s;
    }
    .big-btn:hover {
        background: #00f3ff;
        color: black;
        box-shadow: 0 0 20px #00f3ff;
    }

    /* THE ORB BUTTON CONTAINER */
    .element-container:has(#orb) {
        display: flex;
        justify-content: center;
    }

    /* Hide Streamlit Header */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- 5. AUDIO ENGINE ---
def play_friday_voice(text):
    """Generates audio and forces it to play via HTML."""
    try:
        # Generate Audio
        filename = f"audio_{int(time.time())}.mp3"
        tts = gTTS(text=text, lang='en', tld='co.uk')  # British/Friday voice
        tts.save(filename)

        # Read Audio
        with open(filename, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()

        # Inject Audio Player (Autoplay = True)
        md = f"""
            <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
        os.remove(filename)
    except Exception as e:
        st.error(f"Audio System Failure: {e}")


# --- 6. LOGIC CORE ---
def get_response(text):
    text = text.lower()
    bk = st.session_state.db['booking']

    # 1. RESET
    if any(x in text for x in ["reset", "cancel", "stop"]):
        st.session_state.db['booking'] = {"guests": None, "type": None, "view": None, "confirmed": False}
        return "System reset. Protocols cleared. Ready for new input."

    # 2. START
    if bk['guests'] is None and not any(x in text for x in ["book", "room"]):
        if any(x in text for x in ["hi", "hello", "friday"]):
            return "Hello. I am online. Say 'Book a room' to begin."
        return "Waiting for command. Please say 'Book a room'."

    if bk['guests'] is None:
        if "book" in text or "room" in text:
            return "Acknowledged. Initiating reservation protocol. How many guests will be staying?"

        # Extract Guests
        import re
        nums = re.findall(r'\d+', text)
        w2n = {"one": "1", "two": "2", "three": "3", "four": "4"}
        for k, v in w2n.items():
            if k in text: nums.append(v)

        if nums:
            st.session_state.db['booking']['guests'] = nums[0]
            return f"{nums[0]} guests registered. Please check the dashboard for room types. Would you like Standard, Deluxe, or Presidential?"
        return "Numeric input required. How many guests?"

    # 3. ROOM TYPE
    if bk['type'] is None:
        if "standard" in text:
            st.session_state.db['booking']['type'] = "Standard"
            return "Standard Class selected. Do you prefer a City view?"
        if "deluxe" in text:
            st.session_state.db['booking']['type'] = "Deluxe"
            return "Deluxe Class selected. Do you prefer a Garden view?"
        if "presidential" in text or "suite" in text:
            st.session_state.db['booking']['type'] = "Presidential"
            return "Presidential Suite selected. Do you prefer an Ocean view?"

        return "Please select a room class from the dashboard: Standard, Deluxe, or Presidential."

    # 4. VIEW
    if bk['view'] is None:
        if any(x in text for x in ["city", "garden", "sea", "ocean"]):
            st.session_state.db['booking']['view'] = "Selected View"
            return f"Configuration complete. {st.session_state.db['booking']['type']} room with View. Do you authorize this transaction?"
        else:
            # Assume yes if they say yes to the suggestion
            if "yes" in text:
                st.session_state.db['booking']['view'] = "Standard View"
                return "View confirmed. Do you authorize this transaction?"
            return "Please confirm the view preference."

    # 5. CONFIRM
    if not bk['confirmed']:
        if any(x in text for x in ["yes", "confirm", "ok", "sure"]):
            st.session_state.db['booking']['confirmed'] = True
            st.balloons()
            return "Transaction verified. Reservation uploaded to the Simplotel mainframe. Goodbye."
        return "Awaiting authorization. Say 'Yes' to confirm."

    return "Process complete. Say 'Reset' to start over."


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

        # CLICKING THIS ENABLES THE VOICE
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
        st.write("### CURRENT SESSION")
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
        # START / STOP BUTTONS
        voice_text = speech_to_text(
            start_prompt="🎙️ LISTEN",
            stop_prompt="🛑 PROCESS",
            language='en',
            just_once=False,
            key='voice_control'
        )

    # LOGIC
    user_final = voice_text if voice_text else text_input

    # 1. HANDLE INTRO (Runs Once immediately after Boot)
    if st.session_state.get('intro_needed'):
        intro_text = "System Online. I am Friday, developed by Faizan. I am ready to assist with your booking."
        st.session_state.db['history'].append({"role": "assistant", "content": intro_text})
        play_friday_voice(intro_text)
        st.session_state.intro_needed = False
        st.rerun()

    # 2. HANDLE USER INTERACTION
    if user_final:
        # Log User
        st.session_state.db['history'].append({"role": "user", "content": user_final})

        # Get Response
        bot_reply = get_response(user_final)

        # Log Bot
        st.session_state.db['history'].append({"role": "assistant", "content": bot_reply})

        # Speak
        play_friday_voice(bot_reply)

        # Refresh
        time.sleep(0.2)
        st.rerun()