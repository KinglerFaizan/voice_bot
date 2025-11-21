import streamlit as st
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text
import time
import base64
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Friday AI Concierge",
    page_icon="🧿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. SESSION STATE ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant",
         "content": "Hello! I am Friday, your AI Concierge. How may I assist you with your booking today?"}
    ]
if 'booking_step' not in st.session_state:
    st.session_state.booking_step = 0
if 'booking_data' not in st.session_state:
    st.session_state.booking_data = {"guests": "TBD", "type": "TBD", "view": "TBD"}
if 'system_active' not in st.session_state:
    st.session_state.system_active = True
if 'comm_mode' not in st.session_state:
    st.session_state.comm_mode = None  # None, 'Voice', or 'Text'

# --- 3. FUTURISTIC CSS & BACKGROUND ---
st.markdown("""
<style>
    /* --- BACKGROUND IMAGE --- */
    .stApp {
        background: linear-gradient(to bottom, rgba(0,0,0,0.7), rgba(10,10,30,0.9)), 
                    url('https://images.unsplash.com/photo-1618773928121-c32242e63f39?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #e0e0e0;
    }

    /* --- SELECTION SCREEN BUTTONS --- */
    .big-button {
        width: 100%;
        padding: 20px;
        font-size: 20px;
        border-radius: 15px;
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid #00d4ff;
        color: #00d4ff;
        transition: 0.3s;
    }

    /* --- CHAT BUBBLES --- */
    .stChatMessage {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(0, 255, 204, 0.2);
        border-radius: 15px;
        backdrop-filter: blur(5px);
    }

    /* Icons */
    div[data-testid="chatAvatarIcon-assistant"] { background-color: #00d4ff !important; }
    div[data-testid="chatAvatarIcon-user"] { background-color: #ff0055 !important; }

    /* --- THE "ORB" (Microphone) --- */
    div.stButton > button:first-child {
        background: radial-gradient(circle, #00f2ff 0%, #003344 90%);
        color: white;
        border: 1px solid #00f2ff;
        border-radius: 50%;
        height: 90px;
        width: 90px;
        box-shadow: 0 0 20px #00f2ff;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
    }

    div.stButton > button:first-child:hover {
        transform: scale(1.1);
        box-shadow: 0 0 40px #00f2ff;
    }

    /* Hide Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- 4. AUDIO ENGINE (FRIDAY VOICE) ---
def play_friday_voice(text):
    """Synthesizes speech using a female voice."""
    try:
        file_path = f"friday_{int(time.time())}.mp3"
        # 'en' is usually a female voice in gTTS.
        # 'com' = US accent, 'co.uk' = British.
        tts = gTTS(text=text, lang='en', tld='us')
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
    response = "I'm sorry, I didn't catch that. Could you repeat?"
    terminate = False

    # Reset/Exit
    if "reset" in text or "cancel" in text:
        st.session_state.booking_step = 0
        st.session_state.booking_data = {k: "TBD" for k in st.session_state.booking_data}
        return "System reset. How can I help you now?", False
    if "exit" in text or "bye" in text:
        return "Goodbye! Have a pleasant day.", True

    # Logic Flow
    if step == 0:
        if any(x in text for x in ["book", "room", "hi", "hello", "friday"]):
            st.session_state.booking_step = 1
            response = "Certainly. I can help with that. How many guests will be staying?"
        else:
            response = "I am online. Say 'Book a room' to start the reservation process."

    elif step == 1:  # Guests
        import re
        nums = re.findall(r'\d+', text)
        word_map = {"one": "1", "two": "2", "three": "3", "four": "4"}
        for k, v in word_map.items():
            if k in text: nums.append(v)

        if nums:
            st.session_state.booking_data['guests'] = nums[0]
            st.session_state.booking_step = 2
            response = f"Noted, {nums[0]} guests. Would you prefer an AC or Non-AC room?"
        else:
            response = "I need a number. How many guests?"

    elif step == 2:  # Type
        if "non" in text:
            st.session_state.booking_data['type'] = "Non-AC"
            st.session_state.booking_step = 3
            response = "Non-AC selected. Would you like a Balcony or Pool Access?"
        elif "ac" in text:
            st.session_state.booking_data['type'] = "AC"
            st.session_state.booking_step = 3
            response = "AC room selected. Would you like a Balcony or Pool Access?"
        else:
            response = "Please specify: AC or Non-AC?"

    elif step == 3:  # Feature
        if "pool" in text:
            st.session_state.booking_data['view'] = "Pool Access"
            price = "5000"
        else:
            st.session_state.booking_data['view'] = "Balcony"
            price = "3500"

        st.session_state.booking_step = 4
        response = f"I have configured a {st.session_state.booking_data['type']} room with {st.session_state.booking_data['view']}. Total is {price} credits. Shall I confirm?"

    elif step == 4:  # Confirm
        if "yes" in text or "confirm" in text or "ok" in text:
            st.balloons()
            response = "Booking confirmed. I have uploaded the receipt to your profile. Goodbye!"
            terminate = True
        else:
            st.session_state.booking_step = 0
            response = "Authorization denied. Resetting."

    return response, terminate


# --- 6. MAIN UI LOGIC ---

# HEADER
c1, c2 = st.columns([1, 10])
with c1:
    st.markdown("## 🧿")
with c2:
    st.markdown("## F.R.I.D.A.Y. \n *Simplotel AI Concierge*")
st.divider()

# --- MODE SELECTION SCREEN ---
if st.session_state.comm_mode is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>HOW WOULD YOU LIKE TO CONNECT?</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        # Using columns inside the center column for buttons
        b1, b2 = st.columns(2)
        if b1.button("🎙️ VOICE MODE", use_container_width=True):
            st.session_state.comm_mode = "Voice"
            st.rerun()
        if b2.button("💬 TEXT MODE", use_container_width=True):
            st.session_state.comm_mode = "Text"
            st.rerun()

# --- INTERACTION SCREEN ---
else:
    # Sidebar Data
    with st.sidebar:
        st.title("STATUS")
        st.info(f"MODE: {st.session_state.comm_mode.upper()}")
        st.divider()
        st.metric("GUESTS", st.session_state.booking_data['guests'])
        st.metric("TYPE", st.session_state.booking_data['type'])
        st.metric("VIEW", st.session_state.booking_data['view'])
        st.divider()
        if st.button("END SESSION", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # Chat History
    chat_container = st.container(height=400)
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg['role']):
                st.write(msg['content'])

    # --- INPUT AREA ---
    st.markdown("---")
    user_input = None

    if st.session_state.system_active:

        # CASE 1: VOICE MODE
        if st.session_state.comm_mode == "Voice":
            c1, c2, c3 = st.columns([1, 1, 1])
            with c2:
                st.write("**Tap Orb to Speak**")
                # FAST Recognition: Just once=True returns immediately after silence
                voice_text = speech_to_text(
                    language='en',
                    start_prompt="🧿",
                    stop_prompt="🔴",
                    just_once=True,
                    key='orb'
                )
            if voice_text:
                user_input = voice_text

        # CASE 2: TEXT MODE
        elif st.session_state.comm_mode == "Text":
            text_text = st.chat_input("Type your message to Friday...")
            if text_text:
                user_input = text_text

        # --- PROCESSING LOGIC (Unified) ---
        if user_input:
            # 1. User Msg
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # 2. Get Reply (Immediate processing, no sleep delays)
            bot_reply, terminate = core_logic(user_input)

            # 3. Bot Msg
            st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

            # 4. Audio (Voice Reply is ALWAYS ON for Friday effect)
            play_friday_voice(bot_reply)

            # 5. Terminate?
            if terminate:
                st.session_state.system_active = False
                time.sleep(3)

            st.rerun()

    else:
        st.success("SESSION COMPLETE.")
        if st.button("NEW SESSION"):
            st.session_state.clear()
            st.rerun()