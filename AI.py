import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import os
import time
import base64

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FRIDAY | AI Core",
    page_icon="🧿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. SESSION STATE ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "System Online. I am Friday. Tap the Orb and speak to begin."}
    ]
if 'booking_step' not in st.session_state:
    st.session_state.booking_step = 0
if 'booking_data' not in st.session_state:
    st.session_state.booking_data = {"guests": "TBD", "type": "TBD", "view": "TBD"}
if 'system_ready' not in st.session_state:
    st.session_state.system_ready = False

# --- 3. FUTURISTIC CSS ---
st.markdown("""
<style>
    /* --- BACKGROUND --- */
    .stApp {
        background: linear-gradient(to bottom, rgba(0,0,0,0.8), rgba(10,20,30,0.95)), 
                    url('https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
        font-family: 'Segoe UI', sans-serif;
        color: white;
    }

    /* --- SIDEBAR STATUS MONITOR --- */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 15, 25, 0.9);
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

    /* --- CHAT BUBBLES --- */
    .stChatMessage {
        background: rgba(0, 0, 0, 0.7);
        border: 1px solid rgba(0, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 15px;
    }
    div[data-testid="chatAvatarIcon-assistant"] { background-color: #00d4ff !important; }
    div[data-testid="chatAvatarIcon-user"] { background-color: #ff0055 !important; }

    /* --- THE ORB (RECORDER) --- */
    div.stButton > button:first-child {
        background: radial-gradient(circle, #00f2ff 0%, #000000 90%);
        border: 2px solid #00f2ff;
        color: transparent;
        border-radius: 50%;
        height: 130px;
        width: 130px;
        box-shadow: 0 0 30px #00f2ff, 0 0 60px #00f2ff inset;
        transition: all 0.3s ease;
        margin: 0 auto;
        display: block;
        animation: pulse 3s infinite;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.1);
        box-shadow: 0 0 60px #00f2ff, 0 0 100px #00f2ff inset;
        cursor: pointer;
    }
    div.stButton > button:first-child:active {
        border-color: #ff0055;
        box-shadow: 0 0 60px #ff0055, 0 0 100px #ff0055 inset;
        background: radial-gradient(circle, #ff0055 0%, #220000 90%);
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 242, 255, 0.4); }
        70% { box-shadow: 0 0 0 30px rgba(0, 242, 255, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 242, 255, 0); }
    }

    /* --- INSTRUCTION BOX --- */
    .info-box {
        background: rgba(0, 242, 255, 0.1);
        border: 1px solid #00f2ff;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- 4. AUDIO ENGINE (Hidden Autoplay) ---
def play_friday_audio(text):
    try:
        audio_file = f"friday_{int(time.time())}.mp3"
        tts = gTTS(text=text, lang='en', tld='co.uk')  # British accent
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


# --- 5. CONVERSATION LOGIC ---
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
    st.markdown(
        "<h1 style='text-align: center; color: #00f2ff; text-shadow: 0 0 20px #00f2ff; font-size: 60px;'>FRIDAY AI</h1>",
        unsafe_allow_html=True)

    # INSTRUCTIONS
    st.markdown("""
        <div class='info-box'>
            <h3>⚠️ SYSTEM INSTRUCTIONS</h3>
            <p>1. Click <b>INITIALIZE SYSTEM</b> to enable audio protocols.</p>
            <p>2. Tap the <b>BLUE ORB</b> to activate the microphone.</p>
            <p>3. <b>Speak</b> your request clearly.</p>
            <p>4. <b>Stop Speaking</b> and wait 1-2 seconds. (Do NOT click again).</p>
            <p>The system will auto-detect silence and reply.</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("INITIALIZE SYSTEM", use_container_width=True):
            st.session_state.system_ready = True
            st.rerun()

# --- SCENE 2: MAIN INTERFACE ---
else:
    # --- SIDEBAR DASHBOARD ---
    with st.sidebar:
        st.title("STATUS MONITOR")
        st.markdown("---")
        prog = st.session_state.booking_step * 25
        st.write(f"**SYSTEM INTEGRITY: {prog}%**")
        st.progress(min(prog, 100))

        st.markdown("### RESERVATION DATA")
        st.metric("GUESTS", st.session_state.booking_data['guests'])
        st.metric("CLASS", st.session_state.booking_data['type'])
        st.metric("MODULE", st.session_state.booking_data['view'])

        st.markdown("---")
        if st.button("REBOOT SYSTEM", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # Header
    st.markdown("<h2 style='text-align: center; color: #00f2ff;'>SIMPLOTEL AI CONCIERGE</h2>", unsafe_allow_html=True)
    st.divider()

    # Chat History
    chat_box = st.container(height=350)
    with chat_box:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg['role']):
                st.write(msg['content'])

    # --- THE AUTO-DETECT RECORDER ---
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])

    with c2:
        # THIS HANDLES THE AUTO-STOP LOGIC
        user_text = speech_to_text(
            language='en',
            start_prompt="●",
            stop_prompt="🔴",
            just_once=True,  # Key for auto-stop behavior
            key='orb'
        )
        st.markdown("<p style='text-align: center; color: #00f2ff; letter-spacing: 2px;'>TAP • SPEAK • WAIT</p>",
                    unsafe_allow_html=True)

    # Logic Handling
    if user_text:
        # 1. Display User Input
        st.session_state.chat_history.append({"role": "user", "content": user_text})

        # 2. Get Response
        bot_reply = get_ai_response(user_text)
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

        # 3. Speak (Hidden Player)
        play_friday_audio(bot_reply)

        # 4. Rerun to update chat
        st.rerun()

    # --- AUTO-PLAY WELCOME ---
    if len(st.session_state.chat_history) == 1 and st.session_state.system_ready:
        if 'intro_played' not in st.session_state:
            play_friday_audio("System Online. I am Friday. Tap the Orb and speak to begin.")
            st.session_state.intro_played = True