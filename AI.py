import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import base64
import os
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Simplotel AI",
    page_icon="🧿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. SESSION STATE ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "System Online. Welcome to Simplotel Future Stays. State your request."}
    ]
if 'booking_step' not in st.session_state:
    st.session_state.booking_step = 0
if 'booking_data' not in st.session_state:
    st.session_state.booking_data = {"guests": "TBD", "type": "TBD", "view": "TBD"}
if 'system_online' not in st.session_state:
    st.session_state.system_online = False

# --- 3. FUTURISTIC CSS (Exact Match to your Request) ---
st.markdown("""
<style>
    /* IMPORT FONT */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;400&display=swap');

    /* MAIN BACKGROUND */
    .stApp {
        /* Dark Overlay + Luxury Pool Background */
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url('https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        color: white;
        font-family: 'Roboto', sans-serif;
    }

    /* SIDEBAR STYLING (The Status Monitor) */
    [data-testid="stSidebar"] {
        background-color: rgba(20, 20, 30, 0.9);
        border-right: 1px solid #00ffcc;
    }
    [data-testid="stSidebar"] h1 {
        font-family: 'Orbitron', sans-serif;
        color: #ffffff;
        font-size: 24px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* METRICS IN SIDEBAR */
    div[data-testid="metric-container"] {
        background: transparent;
        border: none;
        color: #00ffcc;
    }
    label[data-testid="stMetricLabel"] {
        color: #aaaaaa !important;
        font-size: 14px !important;
        font-family: 'Orbitron', sans-serif;
    }
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 28px !important;
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 10px #00ffcc;
    }

    /* PROGRESS BAR */
    .stProgress > div > div > div > div {
        background-color: #00ffcc;
        box-shadow: 0 0 10px #00ffcc;
    }

    /* CHAT BUBBLES */
    .stChatMessage {
        background: rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(0, 255, 204, 0.3);
        backdrop-filter: blur(10px);
        border-radius: 0px 20px 20px 20px;
    }
    div[data-testid="chatAvatarIcon-assistant"] { background-color: #00ffcc !important; color: black !important; }
    div[data-testid="chatAvatarIcon-user"] { background-color: #ff0055 !important; }

    /* THE ORB (Microphone) */
    div.stButton > button:first-child {
        background: radial-gradient(circle, #00ffcc 0%, #004433 80%);
        color: transparent;
        border: 2px solid #00ffcc;
        border-radius: 50%;
        height: 100px;
        width: 100px;
        box-shadow: 0 0 30px #00ffcc;
        margin: 0 auto;
        display: block;
        transition: transform 0.2s;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.1);
        box-shadow: 0 0 50px #00ffcc;
    }
    div.stButton > button:first-child:active {
        border-color: #ff0055;
        box-shadow: 0 0 50px #ff0055;
        background: radial-gradient(circle, #ff0055 0%, #440011 80%);
    }

    /* HEADERS */
    .neon-text {
        font-family: 'Orbitron', sans-serif;
        color: #00ffcc;
        text-align: center;
        text-shadow: 0 0 20px #00ffcc;
        font-size: 50px;
        font-weight: bold;
        margin-bottom: 0;
    }
    .sub-text {
        font-family: 'Orbitron', sans-serif;
        color: #ffffff;
        text-align: center;
        letter-spacing: 5px;
        font-size: 14px;
        margin-top: -10px;
        opacity: 0.8;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- 4. AUDIO ENGINE (Autoplay Fix) ---
def autoplay_audio(text):
    """
    Generates audio, converts to base64, and forces autoplay via HTML.
    """
    try:
        audio_file = "response.mp3"
        # 'co.uk' for the sophisticated "Friday" accent
        tts = gTTS(text=text, lang='en', tld='co.uk')
        tts.save(audio_file)

        with open(audio_file, "rb") as f:
            audio_bytes = f.read()

        b64 = base64.b64encode(audio_bytes).decode()

        # Invisible audio player
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
        os.remove(audio_file)
    except Exception:
        pass


# --- 5. LOGIC CORE ---
def core_logic(text_input):
    text = text_input.lower()
    step = st.session_state.booking_step
    response = "Command unrecognized. Please repeat."

    # Global Reset
    if any(x in text for x in ["reset", "cancel", "restart"]):
        st.session_state.booking_step = 0
        st.session_state.booking_data = {k: "TBD" for k in st.session_state.booking_data}
        return "System reset. Protocols cleared."

    if step == 0:
        if any(x in text for x in ["book", "room", "hi", "hello", "friday"]):
            st.session_state.booking_step = 1
            return "Greetings. I can process your reservation. How many guests are checking in?"
        return "System Online. Say 'Book a room' to initialize."

    elif step == 1:  # Guests
        import re
        nums = re.findall(r'\d+', text)
        mapping = {"one": "1", "two": "2", "three": "3", "four": "4"}
        for k, v in mapping.items():
            if k in text: nums.append(v)

        if nums:
            st.session_state.booking_data['guests'] = nums[0]
            st.session_state.booking_step = 2
            return f"{nums[0]} guests confirmed. Do you require an AC or Non-AC unit?"
        return "Numeric input required. How many guests?"

    elif step == 2:  # Type
        if "non" in text:
            st.session_state.booking_data['type'] = "Non-AC"
            st.session_state.booking_step = 3
            return "Non-AC unit selected. Choose add-on: Balcony or Pool Access?"
        elif "ac" in text:
            st.session_state.booking_data['type'] = "AC"
            st.session_state.booking_step = 3
            return "AC unit selected. Choose add-on: Balcony or Pool Access?"
        return "Please select classification: AC or Non-AC."

    elif step == 3:  # View
        if "pool" in text:
            st.session_state.booking_data['view'] = "Pool Access"
        else:
            st.session_state.booking_data['view'] = "Balcony"

        st.session_state.booking_step = 4
        return f"Configuration complete. {st.session_state.booking_data['type']} unit with {st.session_state.booking_data['view']}. Do you authorize this transaction?"

    elif step == 4:  # Confirm
        if any(x in text for x in ["yes", "confirm", "ok", "sure"]):
            st.balloons()
            st.session_state.booking_step = 0
            return "Transaction authorized. Reservation uploaded to database. Goodbye."
        else:
            st.session_state.booking_step = 0
            return "Transaction aborted. Resetting."

    return response


# --- 6. UI LAYOUT ---

# A. INITIALIZATION SCREEN (Crucial for Audio)
if not st.session_state.system_online:
    # Centered "Start" button to unlock browser audio
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='neon-text'>SIMPLOTEL AI CONCIERGE</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-text'>VOICE INTERFACE OFFLINE</p>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("INITIALIZE SYSTEM", use_container_width=True):
            st.session_state.system_online = True
            st.rerun()

# B. MAIN DASHBOARD (After Init)
else:
    # Sidebar: STATUS MONITOR
    with st.sidebar:
        st.markdown("<h1>STATUS MONITOR</h1>", unsafe_allow_html=True)
        st.markdown("---")

        # Progress Bar
        prog = st.session_state.booking_step * 25
        st.write(f"**SYSTEM INTEGRITY: {prog}%**")
        st.progress(min(prog, 100))
        st.markdown("<br>", unsafe_allow_html=True)

        # Metrics
        st.metric("GUESTS", st.session_state.booking_data['guests'])
        st.metric("CLASS", st.session_state.booking_data['type'])
        st.metric("MODULE", st.session_state.booking_data['view'])

        st.markdown("---")
        if st.button("REBOOT", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # Main Area
    st.markdown("<h1 class='neon-text'>SIMPLOTEL AI CONCIERGE</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-text'>VOICE INTERFACE ONLINE</p>", unsafe_allow_html=True)
    st.divider()

    # Chat Area
    chat_box = st.container(height=350)
    with chat_box:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg['role']):
                st.write(msg['content'])

    # The Orb Input
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.write("")
        voice_text = speech_to_text(
            language='en',
            start_prompt="●",
            stop_prompt="■",
            just_once=True,
            key='orb'
        )

    # Logic Handling
    if voice_text:
        # 1. Add User Input
        st.session_state.chat_history.append({"role": "user", "content": voice_text})

        # 2. Process
        bot_reply = core_logic(voice_text)
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

        # 3. Speak & Refresh
        autoplay_audio(bot_reply)
        time.sleep(0.5)  # Tiny delay to allow audio file saving
        st.rerun()