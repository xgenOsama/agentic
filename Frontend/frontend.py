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
                #st.rerun()
                
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
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Custom container for better layout */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Title and header styling */
    .title-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        margin-bottom: 2rem;
        margin-top: 1rem;
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .title-container h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .logo {
        width: 80px;
        height: auto;
        filter: brightness(0) invert(1);
        transition: transform 0.3s ease;
    }
    
    .logo:hover {
        transform: scale(1.05);
    }
    
    /* Chat interface improvements */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 15px !important;
        margin: 0.5rem 0 !important;
        padding: 1rem !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    .stChatMessage[data-testid="chat-message-user"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
        border-left: 4px solid #667eea !important;
    }
    
    /* Chat input styling */
    .stChatInputContainer {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 25px !important;
        border: 2px solid rgba(102, 126, 234, 0.3) !important;
        padding: 0.5rem !important;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stChatInputContainer:focus-within {
        border-color: #667eea !important;
        box-shadow: 0 5px 25px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
    }
    
    /* Sidebar improvements */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%) !important;
        border-right: 2px solid rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Status indicators */
    .stSuccess {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3) !important;
    }
    
    /* Custom info boxes */
    .info-box {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(29, 78, 216, 0.1) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.1);
    }
    
    .warning-box {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.1);
    }
    
    /* Spinner customization */
    .stSpinner {
        border-top-color: #667eea !important;
    }
    
    /* Typography improvements */
    .stMarkdown {
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .title-container h1 {
            font-size: 2rem;
        }
        .main-container {
            margin: 0.5rem;
            padding: 1rem;
        }
    }
    
    /* Animation for smooth transitions */
    * {
        transition: all 0.3s ease;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown(f'<img class="logo" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAiIGhlaWdodD0iODAiIHZpZXdCb3g9IjAgMCA4MCA4MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iNDAiIGN5PSI0MCIgcj0iNDAiIGZpbGw9InVybCgjZ3JhZGllbnQwX2xpbmVhcl8xXzEpIi8+CjxwYXRoIGQ9Ik0yOCAyOEw1MiA1Mk0yOCA1Mkw1MiAyOCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSI0IiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KPGJ1dHRvbiBpZD0iZnVsbHNjcmVlbkJ0biIgb25jbGljaz0idG9nZ2xlRnVsbFNjcmVlbigpIj4KICA8aSBjbGFzcz0iZmFzIGZhLWV4cGFuZCI+PC9pPgo8L2J1dHRvbj4KPGRlZnM+CjxsaW5lYXJHcmFkaWVudCBpZD0iZ3JhZGllbnQwX2xpbmVhcl8xXzEiIHgxPSIwIiB5MT0iMCIgeDI9IjgwIiB5Mj0iODAiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIj4KPHN0b3Agc3RvcC1jb2xvcj0iIzY2N0VFQSIvPgo8c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiM3NjRCQTIiLz4KPC9saW5lYXJHcmFkaWVudD4KPC9kZWZzPgo8L3N2Zz4K" alt="TroubleBuster Logo">', unsafe_allow_html=True)

st.markdown('<div class="title-container"><h1 class="title">🤖 TroubleBuster Agent</h1></div>', unsafe_allow_html=True)

# Show initialization status
if not st.session_state.agent_initialized:
    st.markdown("""
    <div class="info-box">
        <h3 style="margin-top: 0; color: #3b82f6;">🤖 Welcome to TroubleBuster Agent!</h3>
        <p style="margin-bottom: 0;">Your intelligent assistant is ready to help. Send your first message to start the conversation.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="warning-box">
        <p style="margin: 0;"><strong>💡 Note:</strong> The agent will initialize when you send your first message. This may take 30-60 seconds for the first interaction.</p>
    </div>
    """, unsafe_allow_html=True)
elif st.session_state.initialization_error:
    st.error(f"❌ Agent initialization failed: {st.session_state.initialization_error}")
    if st.button("🔄 Retry Initialization", key="retry_init"):
        st.session_state.initialization_error = None
        st.session_state.agent_initialized = False
        st.rerun()
else:
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%); 
                border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 15px; padding: 1rem; margin: 1rem 0; 
                backdrop-filter: blur(5px); box-shadow: 0 4px 15px rgba(16, 185, 129, 0.1);">
        <p style="margin: 0; color: #059669; font-weight: 600;">✅ TroubleBuster Agent is ready and responding!</p>
    </div>
    """, unsafe_allow_html=True)

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_prompt = st.chat_input("💬 Ask anything to TroubleBuster... (e.g., 'Help me troubleshoot my connection')")

if user_prompt:
    # Initialize agent if not already done
    if not st.session_state.agent_initialized:
        with st.spinner("🚀 Initializing TroubleBuster Agent... Please wait..."):
            initialize_agent()
        #if not initialize_agent():
            #st.stop()
    
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
            
            # Show typing indicator
            with st.spinner("🤔 TroubleBuster is thinking..."):
                for event in agent.stream_query(user_id=user_id, session_id=session["id"], message=user_prompt):
                    if "content" in event:
                        if "parts" in event["content"]:
                            parts = event["content"]["parts"]
                            for part in parts:
                                if "text" in part:
                                    text_part += part["text"]
                                    # Update the message in real-time
                                    message_placeholder.markdown(text_part + "▌")  # Add cursor effect
            
            # Remove cursor and show final message
            message_placeholder.markdown(text_part)
        
        st.session_state["messages"].append({"role": "assistant", "content": text_part})
        
    except Exception as e:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%); 
                    border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 15px; padding: 1.5rem; 
                    backdrop-filter: blur(5px); box-shadow: 0 4px 15px rgba(239, 68, 68, 0.1);">
            <h4 style="margin-top: 0; color: #dc2626;">⚠️ Oops! Something went wrong</h4>
            <p style="margin-bottom: 0; color: #7f1d1d;">I encountered an error while processing your request. Please try again or start a new chat.</p>
        </div>
        """, unsafe_allow_html=True)
        st.session_state["messages"].append({"role": "assistant", "content": f"Sorry, I encountered an error: {e}"})
        
# --- SIDEBAR CHAT HISTORY ---
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem; margin-bottom: 1rem; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; color: white;">
        <h2 style="margin: 0; font-family: 'Inter', sans-serif; font-weight: 700;">💬 Chat Hub</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("➕ New Chat", key="new_chat_btn", help="Start a fresh conversation"):
        new_chat() 

    st.markdown("""
    <div style="margin: 1rem 0; padding: 0.5rem 0; border-bottom: 2px solid rgba(102, 126, 234, 0.2);">
        <h3 style="margin: 0; color: #667eea; font-family: 'Inter', sans-serif; font-weight: 600;">🕘 Chat History</h3>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.chat_sessions:
        for chat_id, messages in list(st.session_state.chat_sessions.items()):
            if messages:
                preview = messages[1]["content"][:35] + ("..." if len(messages[1]["content"]) > 35 else "")
            else:
                preview = "Empty chat"

            # Create a container for each chat item
            chat_container = st.container()
            with chat_container:
                cols = st.columns([0.75, 0.25])
                
                # Chat preview button with improved styling
                if cols[0].button(
                    f"💬 {preview}", 
                    key=f"chat_{chat_id}",
                    help=f"Switch to this chat",
                    use_container_width=True
                ):
                    st.session_state.chat_sessions[st.session_state.current_chat_id] = st.session_state.messages
                    st.session_state.current_chat_id = chat_id 
                    st.session_state.messages = st.session_state.chat_sessions[chat_id]
                    st.rerun()

                # Delete button with improved styling
                if cols[1].button("🗑️", key=f"delete_{chat_id}", help="Delete this chat"):
                    del st.session_state.chat_sessions[chat_id]
                    if chat_id == st.session_state.current_chat_id:  
                        st.session_state.current_chat_id = str(uuid.uuid4())
                        st.session_state.messages = []
                        assistant_Opening_msg = "Hi, This is TroubleBuster. How can I help you?"
                        st.session_state["messages"].append({"role": "assistant", "content": assistant_Opening_msg})
                    st.rerun()
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%); 
                    border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 15px; padding: 1.5rem; 
                    text-align: center; backdrop-filter: blur(5px); box-shadow: 0 4px 15px rgba(239, 68, 68, 0.1);">
            <p style="margin: 0; color: #dc2626; font-weight: 500;">📭 No chat history yet</p>
            <small style="color: #7f1d1d;">Start a conversation to see your chat history here!</small>
        </div>
        """, unsafe_allow_html=True)

# Add footer
st.markdown("""
<div style="margin-top: 3rem; padding: 2rem; text-align: center; 
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); 
            border-radius: 15px; border: 1px solid rgba(102, 126, 234, 0.2);">
    <p style="margin: 0; color: #667eea; font-weight: 500;">Powered by TroubleBuster AI • Built with ❤️ using Streamlit</p>
    <small style="color: #8b9dc3;">Your intelligent troubleshooting companion</small>
</div>
""", unsafe_allow_html=True)
