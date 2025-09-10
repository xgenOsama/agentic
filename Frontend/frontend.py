import streamlit as st
import uuid
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from google.auth import default
from google.cloud import aiplatform

# Page setup
st.set_page_config(page_title="TroubleBuster Agent", page_icon="vodafone3.png", layout="centered")

# Agent configuration
#AGENT_ENGINE_ID = "projects/vodaf-aida25lcpm-206/locations/europe-west1/reasoningEngines/300351392336314368"
AGENT_ENGINE_ID = "projects/100938974863/locations/europe-west1/reasoningEngines/6493363829924167680"
 
# Initialize session state for managing multiple chat sessions
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
    assistant_Opening_msg = "Hi, This is TroubleBuster. How can I help you?"
    st.session_state["messages"].append({"role": "assistant", "content": assistant_Opening_msg})

# Agent initialization state (LAZY LOADING)
if "agent_initialized" not in st.session_state:
    st.session_state.agent_initialized = False
if "agent" not in st.session_state:
    st.session_state.agent = None
if "session" not in st.session_state:
    st.session_state.session = None
if "initialization_error" not in st.session_state:
    st.session_state.initialization_error = None

@st.cache_resource
def get_credentials_and_project():
    """Cache credentials to avoid repeated authentication"""
    return default()

def initialize_agent():
    """Initialize the agent and session lazily"""
    try:
        if not st.session_state.agent_initialized:
            with st.spinner("Initializing TroubleBuster Agent..."):
                # Initialize credentials and AI Platform (cached)
                credentials, project = get_credentials_and_project()
                aiplatform.init(project=project, location="europe-west1", credentials=credentials)
                
                # Get agent engine
                agent = agent_engines.get(AGENT_ENGINE_ID)
                st.session_state.agent = agent
                
                # Create session
                user_id = st.session_state.current_chat_id
                session = agent.create_session(user_id=user_id)
                st.session_state.session = session
                
                st.session_state.agent_initialized = True
                st.success("TroubleBuster Agent initialized successfully!")
                st.rerun()
                
    except Exception as e:
        st.session_state.initialization_error = str(e)
        st.error(f"Failed to initialize agent: {e}")
        return False
    return True

def new_chat():
    if st.session_state.messages:
        st.session_state.chat_sessions[st.session_state.current_chat_id] = st.session_state.messages
    st.session_state.current_chat_id = str(uuid.uuid4()) 
    st.session_state.messages = []
    
    # Reset session for new chat if agent is initialized
    if st.session_state.agent:
        user_id = st.session_state.current_chat_id
        session = st.session_state.agent.create_session(user_id=user_id)
        st.session_state.session = session
    
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

# Show initialization status
if not st.session_state.agent_initialized:
    st.info("🤖 **TroubleBuster Agent** is ready to help! Send your first message to start the conversation.")
    st.markdown("""
    <div style="padding: 10px; border-radius: 5px; background-color: #e6f3ff; border-left: 4px solid #0066cc;">
        <small><strong>Note:</strong> The agent will initialize when you send your first message. This may take 30-60 seconds.</small>
    </div>
    """, unsafe_allow_html=True)
elif st.session_state.initialization_error:
    st.error(f"❌ Agent initialization failed: {st.session_state.initialization_error}")
    if st.button("🔄 Retry Initialization"):
        st.session_state.initialization_error = None
        st.session_state.agent_initialized = False
        st.rerun()
else:
    st.success("✅ **TroubleBuster Agent** is ready and responding!")

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_prompt = st.chat_input("Ask anything to TroubleBuster...")

if user_prompt:
    # Initialize agent if not already done
    if not st.session_state.agent_initialized:
        if not initialize_agent():
            st.stop()
    
    st.session_state["messages"].append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Generate and display assistant's response
    try:
        agent = st.session_state.agent
        session = st.session_state.session
        user_id = st.session_state.current_chat_id
        
        text_part = ""
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            for event in agent.stream_query(user_id=user_id, session_id=session["id"], message=user_prompt):
                if "content" in event:
                    if "parts" in event["content"]:
                        parts = event["content"]["parts"]
                        for part in parts:
                            if "text" in part:
                                text_part += part["text"]
                                # Update the message in real-time
                                message_placeholder.markdown(text_part)
        
        st.session_state["messages"].append({"role": "assistant", "content": text_part})
        
    except Exception as e:
        st.error(f"Error generating response: {e}")
        st.session_state["messages"].append({"role": "assistant", "content": f"Sorry, I encountered an error: {e}"})
        
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
