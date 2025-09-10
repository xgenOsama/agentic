import streamlit as st
import uuid

# Page setup
st.set_page_config(page_title="TroubleBuster Agent", page_icon="vodafone3.png", layout="centered")

# Initialize session state for managing multiple chat sessions
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
    assistant_Opening_msg = "Hi, This is TroubleBuster. How can I help you?"
    st.session_state["messages"].append({"role": "assistant", "content": assistant_Opening_msg})


def new_chat():
    if st.session_state.messages:
        st.session_state.chat_sessions[st.session_state.current_chat_id] = st.session_state.messages
    st.session_state.current_chat_id = str(uuid.uuid4()) 
    st.session_state.messages = []
    assistant_Opening_msg = "Hi, This is TroubleBuster. How can I help you?"
    st.session_state["messages"].append({"role": "assistant", "content": assistant_Opening_msg})
    st.rerun() 


st.markdown("""
<style>
    body {
        background-color: white;
    }
    .title-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
        margin-bottom: 10px;
        margin-top: 10px;
    }
    .title-container h1 {
        width: 100%;
        text-align: left;
        margin: 0;
        color: #000000;
        font-size: 2.2em; 
    }
    .logo {
        position: left;
        left: 2px;
        width: 70px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(f'<img class="logo" src="https://vodafone.sharepoint.com/:i:/r/sites/Branding2/Shared%20Documents/Brand%20Guidelines%20%26%20Images/Logos/VOIS_LOGO_gradient.png?csf=1&web=1&e=wRlfI3">', unsafe_allow_html=True)

st.markdown('<div class="title-container"><h1 class="title">TroubleBuster Agent</h1></div>', unsafe_allow_html=True)

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_prompt = st.chat_input("Ask anything to TroubleBuster...")


if user_prompt:
    st.session_state["messages"].append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Generate and display assistant's response (placeholder)
    assistant_response = "This is a placeholder response from the assistant."
    st.session_state["messages"].append({"role": "assistant", "content": assistant_response})
    with st.chat_message("assistant"):
        st.markdown(assistant_response)
        
# --- SIDEBAR CHAT HISTORY ---
with st.sidebar:
    if st.button("➕ New Chat"):
        new_chat() 

    st.markdown("## 🕘 Chat History") 

    if st.session_state.chat_sessions:
        for chat_id, messages in list(st.session_state.chat_sessions.items()):
            if messages:
                preview = messages[1]["content"][:30] + ("..." if len(messages[1]["content"]) > 30 else "")
            else:
                preview = "Empty chat"

            cols = st.columns([0.8, 0.2])  


            if cols[0].button(preview, key=f"chat_{chat_id}"):
                st.session_state.chat_sessions[st.session_state.current_chat_id] = st.session_state.messages
                st.session_state.current_chat_id = chat_id 
                st.session_state.messages = st.session_state.chat_sessions[chat_id]
                st.rerun()


            if cols[1].button("✖", key=f"delete_{chat_id}"):
                del st.session_state.chat_sessions[chat_id]
                if chat_id == st.session_state.current_chat_id:  
                    st.session_state.current_chat_id = str(uuid.uuid4())
                    st.session_state.messages = []
                st.rerun()
    else:

        st.markdown("""
        <div style="padding: 10px; border-radius: 5px; background-color: #ffe6e6; color: #b22222; border: 1px solid #b22222;">
            No history yet.
        </div>
        """, unsafe_allow_html=True)
