import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import time
import base64

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FRIDAY AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. SESSION STATE ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "System Online. I am Friday. I am listening."}
    ]
if 'booking_step' not in st.session_state:
    st.session_state.booking_step = 0
if 'booking_data' not in st.session_state:
    st.session_state.booking_data = {"guests": "TBD", "type": "TBD", "view": "TBD"}
if 'system_ready' not in st.session_state:
    st.session_state.system_ready = False

# --- 3. CSS STYLING ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(to bottom, rgba(0,0,0,0.8), rgba(10,20,30,0.95)), 
                    url('https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Chat & Sidebar Styles */
    .stChatMessage {
        background: rgba(0, 0, 0, 0.7);
        border: 1px solid rgba(0, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 15px;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(10, 15, 25, 0.95);
        border-right: 1px solid #00f2ff;
    }
    div[data-testid="metric-container"] {
        background: rgba(0, 242, 255, 0.05);
        border: 1px solid #00f2ff;
        color: #00f2ff;
        border-radius: 5px;
        padding: 10px;
    }
    label[data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; }

    /* THE ORB */
    div.stButton > button:first-child {
        background: radial-gradient(circle, #00f2ff 0%, #000000 90%);
        border: 2px solid #00f2ff;
        color: transparent;
        border-radius: 50%;
        height: 120px;
        width: 120px;
        box-shadow: 0 0 30px #00f2ff, 0 0 60px #00f2ff inset;
        transition: all 0.2s ease;
        margin: 0 auto;
        display: block;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.05);
        box-shadow: 0 0 50px #00f2ff, 0 0 80px #00f2ff inset;
    }
    div.stButton > button:first-child:active {
        border-color: #ff0055;
        box-shadow: 0 0 60px #ff0055, 0 0 100px #ff0055 inset;
        background: radial-gradient(circle, #ff0055 0%, #220000 90%);
    }

    /* INSTRUCTION BOX */
    .info-box {
        border: 1px solid #00f2ff;
        padding: 15px;
        border-radius: 10px;
        background: rgba(0,0,0,0.5);
        text-align: center;
        margin-bottom: 20px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- 4. AUDIO ENGINE (OPTIMIZED) ---
def play_friday_audio(text):
    """Generates and plays audio immediately."""
    try:
        audio_file = f"audio_{int(time.time())}.mp3"
        tts = gTTS(text=text, lang='en', tld='co.uk')
        tts.save(audio_file)

        with open(audio_file, "rb") as f:
            audio_bytes = f.read()
        b64 = base64.b64encode(audio_bytes).decode()

        md = f"""
            <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
        os.remove(audio_file)
    except Exception:
        pass


# --- 5. LOGIC CORE ---
def get_ai_response(text_input):
    text = text_input.lower()
    step = st.session_state.booking_step

    if any(x in text for x in ["reset", "cancel", "stop"]):
        st.session_state.booking_step = 0
        st.session_state.booking_data = {k: "TBD" for k in st.session_state.booking_data}
        return "System reset. Waiting for new input."

    if step == 0:
        if any(x in text for x in ["book", "room", "hi", "hello"]):
            st.session_state.booking_step = 1
            return "Greetings. How many guests will be staying?"
        return "I am Friday. Say 'Book a room' to initialize."

    elif step == 1:
        import re
        nums = re.findall(r'\d+', text)
        w2n = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5"}
        for k, v in w2n.items():
            if k in text: nums.append(v)

        if nums:
            st.session_state.booking_data['guests'] = nums[0]
            st.session_state.booking_step = 2
            return f"{nums[0]} guests confirmed. AC or Non-AC suite?"
        return "I need a number. How many guests?"

    elif step == 2:
        if "non" in text:
            st.session_state.booking_data['type'] = "Non-AC"
            st.session_state.booking_step = 3
            return "Non-AC selected. Do you require a Balcony or Pool Access?"
        elif "ac" in text:
            st.session_state.booking_data['type'] = "AC"
            st.session_state.booking_step = 3
            return "AC selected. Do you require a Balcony or Pool Access?"
        return "Please choose: AC or Non-AC."

    elif step == 3:
        if "pool" in text:
            st.session_state.booking_data['view'] = "Pool Access"
        else:
            st.session_state.booking_data['view'] = "Balcony"

        st.session_state.booking_step = 4
        return f"Configuration complete: {st.session_state.booking_data['type']} suite with {st.session_state.booking_data['view']}. Authorize?"

    elif step == 4:
        if any(x in text for x in ["yes", "confirm", "ok", "sure"]):
            st.balloons()
            st.session_state.booking_step = 0
            return "Authorization Verified. Reservation confirmed. Goodbye."
        else:
            st.session_state.booking_step = 0
            return "Authorization denied. Resetting."

    return "Input unclear. Please repeat."


# --- 6. UI LAYOUT ---

# --- SCENE 1: SYSTEM BOOT ---
if not st.session_state.system_ready:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #00f2ff; font-size: 60px;'>FRIDAY AI</h1>",
                unsafe_allow_html=True)

    st.markdown("""
        <div class='info-box'>
            <h3>🚀 SYSTEM INITIALIZATION</h3>
            <p>1. Click <b>INITIALIZE SYSTEM</b> below to enable Voice Protocols.</p>
            <p>2. Tap the <b>BLUE ORB</b> to Speak.</p>
            <p>3. <b>Wait 1 second</b> after speaking for auto-detection.</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("INITIALIZE SYSTEM", use_container_width=True):
            st.session_state.system_ready = True
            # Trigger welcome voice next run
            st.session_state.trigger_welcome = True
            st.rerun()

# --- SCENE 2: MAIN INTERFACE ---
else:
    # DASHBOARD
    with st.sidebar:
        st.title("STATUS MONITOR")
        st.markdown("---")
        prog = st.session_state.booking_step * 25
        st.write(f"**INTEGRITY: {prog}%**")
        st.progress(min(prog, 100))

        st.markdown("### DATA FEED")
        st.metric("GUESTS", st.session_state.booking_data['guests'])
        st.metric("CLASS", st.session_state.booking_data['type'])
        st.metric("MODULE", st.session_state.booking_data['view'])

        st.markdown("---")
        if st.button("REBOOT SYSTEM", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # MAIN CHAT
    st.markdown("<h2 style='text-align: center; color: #00f2ff;'>SIMPLOTEL AI CONCIERGE</h2>", unsafe_allow_html=True)
    st.divider()

    chat_box = st.container(height=350)
    with chat_box:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg['role']):
                st.write(msg['content'])

    # INPUT AREA (Voice + Text)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])

    # 1. VOICE ORB
    with c2:
        voice_text = speech_to_text(
            language='en',
            start_prompt="●",
            stop_prompt="🔴",
            just_once=True,
            key='orb'
        )

    # 2. TEXT BAR (Added back as requested)
    text_text = st.chat_input("Type your command here...")

    # PROCESS LOGIC
    user_input = voice_text if voice_text else text_text

    if user_input:
        # Display User
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Logic
        bot_reply = get_ai_response(user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

        # Speak (Always speak regardless of input method)
        play_friday_audio(bot_reply)

        # Refresh
        st.rerun()

    # AUTO-PLAY WELCOME (Runs once after init)
    if st.session_state.get('trigger_welcome'):
        play_friday_audio("System Online. I am Friday. I am listening.")
        st.session_state.trigger_welcome = False