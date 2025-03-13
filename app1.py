import streamlit as st
import subprocess
import threading
import time
import os

# File to store conversation history
CONVERSATION_FILE = "conversation.txt"

def run_backend(language):
    """Run the backend code based on the selected language."""
    if language == "English":
        subprocess.run(["python", "main.py"])
    elif language == "Telugu":
        subprocess.run(["python", "telugu.py"])

def stop_backend():
    """Stop the backend by creating a stop flag file."""
    with open("stop_flag.txt", "w") as f:
        f.write("stop")

def read_conversation():
    """Read the conversation from the file."""
    if os.path.exists(CONVERSATION_FILE):
        with open(CONVERSATION_FILE, "r", encoding="utf-8") as f:
            return f.readlines()
    return []

# Streamlit app
def main():
    st.set_page_config(page_title="Panda Voice Assistant", page_icon="🐼", layout="centered")
    
    st.markdown("""
    <style>
    div.stButton > button {
        background-color: green !important;
        color: white !important;
        border-radius: 5px !important;
        border: none !important;
        padding: 10px 20px !important;
        font-size: 16px !important;
        cursor: pointer !important;
    }
    div.stButton > button:hover {
        background-color: darkgreen !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;'>🐼 Panda Voice Assistant</h1>", unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; font-size: 80px;">🐼</div>', unsafe_allow_html=True)

    if "assistant_active" not in st.session_state:
        st.session_state.assistant_active = False
    if "language_selected" not in st.session_state:
        st.session_state.language_selected = False

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Start Panda Assistant", key="start_button", help="Start the Panda Voice Assistant"):
            st.session_state.assistant_active = True
            st.session_state.language_selected = False
            st.write("🎤 Please select a language to proceed.")
    with col2:
        if st.button("🚑 Stop Panda Assistant", key="stop_button", help="Stop the Panda Voice Assistant"):
            if st.session_state.assistant_active:
                stop_backend()
                st.session_state.assistant_active = False
                st.session_state.language_selected = False
                st.write("🚑 Panda Assistant has been stopped.")
            else:
                st.write("🤔 Panda Assistant is not running.")

    if st.session_state.assistant_active and not st.session_state.language_selected:
        st.markdown("<h3 style='text-align: center;'>Choose Language</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("English", key="english_button", help="Select English as the language"):
                st.session_state.language = "English"
                st.session_state.language_selected = True
        with col2:
            if st.button("Telugu", key="telugu_button", help="Select Telugu as the language"):
                st.session_state.language = "Telugu"
                st.session_state.language_selected = True

    if st.session_state.assistant_active and st.session_state.language_selected:
        if os.path.exists("stop_flag.txt"):
            os.remove("stop_flag.txt")
        if os.path.exists(CONVERSATION_FILE):
            os.remove(CONVERSATION_FILE)

        st.write(f"🎤 Listening for wake word in {st.session_state.language}...")
        backend_thread = threading.Thread(target=run_backend, args=(st.session_state.language,))
        backend_thread.start()

        while backend_thread.is_alive():
            time.sleep(1)

        st.write("✅ Panda Assistant is ready for commands.")

    st.sidebar.markdown("## Conversation History")
    show_history = st.sidebar.checkbox("View Conversation", key="show_history_checkbox")

    if show_history:
        conversation = read_conversation()
        if conversation:
            st.sidebar.markdown("### 💬 Conversation History")
            st.sidebar.text("\n".join([line.strip() for line in conversation]))
        else:
            st.sidebar.write("No conversation history available.")

if __name__ == "__main__":
    main()
