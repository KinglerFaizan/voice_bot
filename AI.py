import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import time
import base64
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Simplotel AI Core",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. SESSION STATE ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "SYSTEM ONLINE. WELCOME TO SIMPLOTEL FUTURE STAYS. STATE YOUR REQUEST."}
    ]
if 'booking_step' not in st.session_state:
    st.session_state.booking_step = 0
if 'booking_data' not in st.session_state:
    st.session_state.booking_data = {"guests": "TBD", "type": "TBD", "view": "TBD"}
if 'system_active' not in st.session_state:
    st.session_state.system_active = True

# --- 3. FUTURISTIC CSS & BACKGROUND ---
st.markdown("""
<style>
    /* --- BACKGROUND IMAGE --- */
    .stApp {
        /* Futuristic Hotel Image with Dark Overlay */
        background: linear-gradient(to bottom, rgba(0,0,0,0.8), rgba(10,10,30,0.9)), 
                    url('https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #e0e0e0;
    }

    /* --- GLASSMORPHISM SIDEBAR --- */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* --- CHAT BUBBLES --- */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 255, 0.1);
        border-radius: 15px;
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    }

    /* Bot Icon Color */
    div[data-testid="chatAvatarIcon-assistant"] {
        background-color: #00d4ff !important;
    }

    /* User Icon Color */
    div[data-testid="chatAvatarIcon-user"] {
        background-color: #ff0055 !important;
    }

    /* --- THE "ORB" (Microphone) --- */
    div.stButton > button:first-child {
        background: radial-gradient(circle, #00f2ff 0%, #003344 90%);
        color: transparent; /* Hide text */
        border: 1px solid #00f2ff;
        border-radius: 50%;
        height: 90px;
        width: 90px;
        box-shadow: 0 0 15px #00f2ff, 0 0 30px #00f2ff inset;
        transition: all 0.4s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        animation: pulse 2s infinite;
    }

    /* Hover Effect */
    div.stButton > button:first-child:hover {
        transform: scale(1.1);
        box-shadow: 0 0 30px #00f2ff, 0 0 60px #00f2ff inset;
    }

    /* Active (Recording) Effect */
    div.stButton > button:first-child:active {
        background: radial-gradient(circle, #ff0055 0%, #440011 90%);
        box-shadow: 0 0 30px #ff0055, 0 0 60px #ff0055 inset;
        border-color: #ff0055;
    }

    /* Orb Animation */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 242, 255, 0.4); }
        70% { box-shadow: 0 0 0 20px rgba(0, 242, 255, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 242, 255, 0); }
    }

    /* --- METRIC CARDS --- */
    div[data-testid="metric-container"] {
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid rgba(0, 212, 255, 0.3);
        padding: 15px;
        border-radius: 10px;
    }
    label[data-testid="stMetricLabel"] {
        color: #00d4ff !important;
    }

    /* Hide Default Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

</style>
""", unsafe_allow_html=True)


# --- 4. AUDIO ENGINE ---
def play_ai_voice(text):
    """Synthesizes speech and auto-plays it."""
    try:
        file_path = f"voice_{int(time.time())}.mp3"
        tts = gTTS(text=text, lang='en', tld='co.uk')  # British accent for that "Jarvis" feel
        tts.save(file_path)

        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()

        md = f"""
            <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
        os.remove(file_path)
    except Exception:
        pass


# --- 5. INTELLIGENCE CORE ---
def core_logic(text_input):
    text = text_input.lower()
    step = st.session_state.booking_step
    response = "DATA CORRUPT. PLEASE REPEAT COMMAND."
    terminate = False

    # Reset/Exit
    if "reset" in text or "cancel" in text:
        st.session_state.booking_step = 0
        st.session_state.booking_data = {k: "TBD" for k in st.session_state.booking_data}
        return "SYSTEM REBOOTED. READY FOR NEW INPUT.", False
    if "exit" in text or "bye" in text:
        return "TERMINATING SESSION. GOODBYE.", True

    # Logic Flow
    if step == 0:
        if any(x in text for x in ["book", "room", "hi", "hello"]):
            st.session_state.booking_step = 1
            response = "GREETINGS. INITIATING RESERVATION PROTOCOL. STATE NUMBER OF GUESTS."
        else:
            response = "STANDBY. PLEASE SAY 'BOOK A ROOM' TO ACTIVATE."

    elif step == 1:  # Guests
        import re
        nums = re.findall(r'\d+', text)
        word_map = {"one": "1", "two": "2", "three": "3", "four": "4"}
        for k, v in word_map.items():
            if k in text: nums.append(v)

        if nums:
            st.session_state.booking_data['guests'] = nums[0]
            st.session_state.booking_step = 2
            response = f"{nums[0]} HUMAN GUESTS LOGGED. SELECT ENVIRONMENT: AC OR NON-AC?"
        else:
            response = "NUMERIC VALUE REQUIRED. HOW MANY GUESTS?"

    elif step == 2:  # Type
        if "non" in text:
            st.session_state.booking_data['type'] = "NON-AC"
            st.session_state.booking_step = 3
            response = "NON-AC SELECTED. CHOOSE UPGRADE: BALCONY OR POOL ACCESS?"
        elif "ac" in text:
            st.session_state.booking_data['type'] = "AC"
            st.session_state.booking_step = 3
            response = "AC ENVIRONMENT SELECTED. CHOOSE UPGRADE: BALCONY OR POOL ACCESS?"
        else:
            response = "BINARY CHOICE REQUIRED: AC OR NON-AC."

    elif step == 3:  # Feature
        if "pool" in text:
            st.session_state.booking_data['view'] = "POOL ACCESS"
            price = "5000 CREDITS"
        else:
            st.session_state.booking_data['view'] = "BALCONY"
            price = "3500 CREDITS"

        st.session_state.booking_step = 4
        response = f"CONFIGURATION COMPLETE. ROOM: {st.session_state.booking_data['type']} WITH {st.session_state.booking_data['view']}. TOTAL: {price}. AUTHORIZE?"

    elif step == 4:  # Confirm
        if "yes" in text or "confirm" in text or "ok" in text:
            st.balloons()
            response = "AUTHORIZATION VERIFIED. RESERVATION CONFIRMED. TERMINATING CONNECTION."
            terminate = True
        else:
            st.session_state.booking_step = 0
            response = "NEGATIVE. RESETTING PROTOCOLS."

    return response, terminate


# --- 6. UI LAYOUT ---

# Sidebar Dashboard
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/5968/5968957.png", width=60)
    st.title("STATUS MONITOR")
    st.markdown("---")

    # Progress Bar with Neon Color
    st.markdown(
        """
        <style>
            .stProgress > div > div > div > div {
                background-color: #00d4ff;
            }
        </style>""",
        unsafe_allow_html=True,
    )

    prog = st.session_state.booking_step * 25
    st.progress(min(prog, 100))
    st.caption(f"SYSTEM INTEGRITY: {prog}%")

    st.divider()

    # Glassmorphism Metrics
    m1, m2 = st.columns(2)
    m1.metric("GUESTS", st.session_state.booking_data['guests'])
    m2.metric("CLASS", st.session_state.booking_data['type'])
    st.metric("MODULE", st.session_state.booking_data['view'])

    st.markdown("---")
    if st.button("REBOOT SYSTEM", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# Main Content
if st.session_state.system_active:
    # Header
    st.markdown(
        "<h1 style='text-align: center; color: #00d4ff; text-shadow: 0 0 10px #00d4ff;'>SIMPLOTEL AI CONCIERGE</h1>",
        unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #aaaaaa; letter-spacing: 2px;'>VOICE INTERFACE ONLINE</p>",
                unsafe_allow_html=True)

    st.divider()

    # Chat Area
    chat_box = st.container()
    with chat_box:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg['role']):
                st.write(msg['content'])

    st.markdown("<div style='height: 50px'></div>", unsafe_allow_html=True)

    # The "Orb" Input Area
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.write("⬇️ **TAP ORB TO SPEAK**")
        # The "Orb"
        user_voice_input = speech_to_text(
            language='en',
            start_prompt="●",
            stop_prompt="■",
            just_once=True,
            key='orb_input'
        )

    # Logic Processor
    if user_voice_input:
        # 1. Show User Input
        st.session_state.chat_history.append({"role": "user", "content": user_voice_input})

        # 2. Process
        with st.spinner("ANALYZING WAVEFORMS..."):
            time.sleep(0.5)  # Sci-fi delay
            bot_reply, should_end = core_logic(user_voice_input)

        # 3. Reply
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        play_ai_voice(bot_reply)

        # 4. End Session Logic
        if should_end:
            st.session_state.system_active = False
            time.sleep(3)  # Wait for audio to finish

        st.rerun()

else:
    # Terminated Screen
    st.markdown("""
        <div style='text-align: center; margin-top: 100px;'>
            <h1 style='color: #ff0055; font-size: 60px;'>SESSION ENDED</h1>
            <p>THANK YOU FOR CHOOSING SIMPLOTEL.</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("ESTABLISH NEW LINK"):
            st.session_state.clear()
            st.rerun()