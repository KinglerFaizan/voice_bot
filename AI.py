import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import time
import base64

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FRIDAY AI",
    page_icon="🧿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. SESSION STATE ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "System Online. I am Friday. How may I assist with your reservation?"}
    ]
if 'booking_step' not in st.session_state:
    st.session_state.booking_step = 0
if 'booking_data' not in st.session_state:
    st.session_state.booking_data = {"guests": "TBD", "type": "TBD", "view": "TBD"}
if 'system_initialized' not in st.session_state:
    st.session_state.system_initialized = False
if 'play_intro' not in st.session_state:
    st.session_state.play_intro = False

# --- 3. FUTURISTIC CSS ---
st.markdown("""
<style>
    /* BACKGROUND */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(10,20,40,0.95)), 
                    url('https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
        color: #e0e0e0;
        font-family: 'Segoe UI', sans-serif;
    }

    /* CHAT BUBBLES */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 255, 0.1);
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    div[data-testid="chatAvatarIcon-assistant"] { background-color: #00d4ff !important; }
    div[data-testid="chatAvatarIcon-user"] { background-color: #ff0055 !important; }

    /* SIDEBAR STATUS MONITOR */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 15, 20, 0.9);
        border-right: 1px solid #00d4ff;
    }
    div[data-testid="metric-container"] {
        background: rgba(0, 212, 255, 0.05);
        border: 1px solid #00d4ff;
        color: #00d4ff;
        border-radius: 5px;
        padding: 10px;
    }
    label[data-testid="stMetricLabel"] { color: #aaaaaa !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; }

    /* THE ORB (Microphone) */
    div.stButton > button:first-child {
        background: radial-gradient(circle, #00f2ff 0%, #003344 100%);
        color: transparent;
        border: 2px solid #00f2ff;
        border-radius: 50%;
        height: 100px;
        width: 100px;
        box-shadow: 0 0 20px #00f2ff, 0 0 40px #00f2ff inset;
        transition: 0.3s;
        margin: 0 auto;
        display: block;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.1);
        box-shadow: 0 0 50px #00f2ff, 0 0 80px #00f2ff inset;
    }
    div.stButton > button:first-child:active {
        background: radial-gradient(circle, #ff0055 0%, #440011 100%);
        border-color: #ff0055;
    }

    /* Start Button Style */
    .big-btn {
        font-size: 30px;
        padding: 20px;
        color: #00d4ff;
        border: 2px solid #00d4ff;
        background: transparent;
        width: 100%;
        cursor: pointer;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- 4. AUDIO ENGINE ---
def play_audio(text):
    """Generates and plays audio (Hidden Player)."""
    try:
        audio_file = f"voice_{int(time.time())}.mp3"
        # British accent for Friday
        tts = gTTS(text=text, lang='en', tld='co.uk')
        tts.save(audio_file)

        with open(audio_file, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()

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
    response = "Command unclear. Please repeat."

    # RESET
    if any(x in text for x in ["reset", "cancel", "restart"]):
        st.session_state.booking_step = 0
        st.session_state.booking_data = {k: "TBD" for k in st.session_state.booking_data}
        return "System reset. Waiting for protocols."

    # FLOW
    if step == 0:
        if any(x in text for x in ["book", "room", "hi", "hello", "friday"]):
            st.session_state.booking_step = 1
            return "Greetings. I can process your reservation. How many guests are checking in?"
        return "I am Friday. Say 'Book a room' to initialize protocols."

    elif step == 1:  # GUESTS
        import re
        nums = re.findall(r'\d+', text)
        map_w = {"one": "1", "two": "2", "three": "3", "four": "4"}
        for k, v in map_w.items():
            if k in text: nums.append(v)

        if nums:
            st.session_state.booking_data['guests'] = nums[0]
            st.session_state.booking_step = 2
            return f"{nums[0]} guests confirmed. Do you require an AC or Non-AC unit?"
        return "Numeric input required. How many guests?"

    elif step == 2:  # TYPE
        if "non" in text:
            st.session_state.booking_data['type'] = "Non-AC"
            st.session_state.booking_step = 3
            return "Non-AC unit selected. Choose add-on: Balcony or Pool Access?"
        elif "ac" in text:
            st.session_state.booking_data['type'] = "AC"
            st.session_state.booking_step = 3
            return "AC unit selected. Choose add-on: Balcony or Pool Access?"
        return "Please select classification: AC or Non-AC."

    elif step == 3:  # VIEW
        if "pool" in text:
            st.session_state.booking_data['view'] = "Pool Access"
        else:
            st.session_state.booking_data['view'] = "Balcony"

        st.session_state.booking_step = 4
        return f"Configuration complete. {st.session_state.booking_data['type']} unit with {st.session_state.booking_data['view']}. Do you authorize this transaction?"

    elif step == 4:  # CONFIRM
        if any(x in text for x in ["yes", "confirm", "ok", "sure"]):
            st.balloons()
            st.session_state.booking_step = 0
            return "Transaction authorized. Reservation uploaded to database. Goodbye."
        else:
            st.session_state.booking_step = 0
            return "Transaction aborted. Resetting."

    return response


# --- 6. UI LAYOUT ---

# --- SCENE 1: INITIALIZATION (REQUIRED FOR AUDIO) ---
if not st.session_state.system_initialized:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br><br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #00f2ff; text-shadow: 0 0 20px #00f2ff;'>SIMPLOTEL AI</h1>",
                    unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: white;'>VOICE INTERFACE OFFLINE</p>", unsafe_allow_html=True)

        # This button is the "Key" that unlocks audio in the browser
        if st.button("ACTIVATE SYSTEM", use_container_width=True):
            st.session_state.system_initialized = True
            st.session_state.play_intro = True  # Trigger intro voice
            st.rerun()

# --- SCENE 2: MAIN INTERFACE ---
else:
    # SIDEBAR DASHBOARD
    with st.sidebar:
        st.markdown("### STATUS MONITOR")
        st.markdown("---")
        prog = st.session_state.booking_step * 25
        st.write(f"**INTEGRITY: {prog}%**")
        st.progress(min(prog, 100))
        st.divider()

        m1, m2 = st.columns(2)
        m1.metric("GUESTS", st.session_state.booking_data['guests'])
        m2.metric("CLASS", st.session_state.booking_data['type'])
        st.metric("MODULE", st.session_state.booking_data['view'])

        st.divider()
        if st.button("REBOOT", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # MAIN CHAT AREA
    st.markdown("## 🧿 F.R.I.D.A.Y.")

    chat_box = st.container(height=400)
    with chat_box:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg['role']):
                st.write(msg['content'])

    # INPUT AREA (Fixed at bottom)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])

    with c2:
        st.write("**TAP ORB TO SPEAK**")
        voice_text = speech_to_text(
            language='en',
            start_prompt="●",
            stop_prompt="■",
            just_once=True,
            key='orb'
        )

    # Text Input Fallback
    text_text = st.chat_input("Or type commands here...")

    # UNIFIED LOGIC HANDLER
    user_input = voice_text if voice_text else text_text

    # 1. PLAY INTRO (Only once on startup)
    if st.session_state.play_intro:
        play_audio("System Online. I am Friday. How may I assist with your reservation?")
        st.session_state.play_intro = False

    # 2. PROCESS USER INPUT
    if user_input:
        # Show User
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Process
        bot_reply = core_logic(user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

        # Speak
        play_audio(bot_reply)

        # Refresh
        st.rerun()