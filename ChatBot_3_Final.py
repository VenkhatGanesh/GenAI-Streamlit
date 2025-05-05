import streamlit as st
import requests
import json
import uuid
import time
from datetime import datetime
import logging
import sys
import io
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(
    page_title="Enterprise Assistant Hub",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for dark theme
st.markdown("""
<style>
    .main {
        background-color: #1E1E1E;
        color: #E0E0E0;
    }
    .stTextInput, .stTextArea {
        background-color: #2D2D2D;
        color: #E0E0E0;
    }
    .stButton>button {
        background-color: #4F4F4F;
        color: #E0E0E0;
    }
    .stButton>button:hover {
        background-color: #616161;
        color: #FFFFFF;
    }
    .stSidebar {
        background-color: #252526;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message-user {
        background-color: #2C5282;
        border-left: 5px solid #4299E1;
    }
    .chat-message-assistant {
        background-color: #2D3748;
        border-left: 5px solid #A0AEC0;
    }
    .chat-message-content {
        margin-top: 0.5rem;
        white-space: pre-wrap;
    }
    .chat-timestamp {
        font-size: 0.75rem;
        color: #A0AEC0;
    }
    .log-entry {
        margin-bottom: 0.5rem;
        padding: 0.5rem;
        border-radius: 0.25rem;
        font-family: monospace;
        font-size: 0.85rem;
    }
    .log-info {
        background-color: #2D3748;
        border-left: 3px solid #4299E1;
    }
    .log-error {
        background-color: #742A2A;
        border-left: 3px solid #F56565;
    }
    .log-time {
        font-size: 0.75rem;
        color: #A0AEC0;
    }
    .assistant-title {
        font-size: 1.25rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #90CDF4;
    }
    .assistant-description {
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
        color: #CBD5E0;
    }
    .stSidebar [data-testid="stSidebarNav"] {
        background-color: #252526;
    }
    section[data-testid="stSidebar"] > div {
        background-color: #252526;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #2D3748;
        border-radius: 4px 4px 0px 0px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4A5568;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = {}

if 'session_ids' not in st.session_state:
    st.session_state.session_ids = {}

if 'current_assistant' not in st.session_state:
    st.session_state.current_assistant = None

if 'logs' not in st.session_state:
    st.session_state.logs = {}

# Define assistants
assistants = {
    "shizoku": {
        "name": "Shizoku - The CRM Assistant",
        "description": "Your dedicated sales assistant for Salesforce CRM operations",
        "url": "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/salesforce_agent_driver_VG_api",
        "auth": "Bearer z7gxfLKED6GRxY4Fdwcd9gcoWgJd5Q4c",
        "placeholder": "Ask about Salesforce data, opportunities, or customer information..."
    },
    "tomodachi": {
        "name": "Tomodachi - HR Assistant",
        "description": "Your helpful HR companion for employee information and workplace procedures",
        "url": "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/HRASSIST_agent_driver_VG_api",
        "auth": "Bearer 6BJ0xGbyAourBtiSgp7c2AZrvGvQ4eEd",
        "placeholder": "Ask about HR policies, employee information, or workplace procedures..."
    },
    "zaiko": {
        "name": "Zaiko - The Inventory Manager",
        "description": "Your inventory specialist for gadget stock information and availability",
        "url": "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/GadgetStore_agent_driver_VG_api",
        "auth": "Bearer JRJ5TFPwQMshJqxGVr0IQY5I5qYRGcDd",
        "placeholder": "Ask about inventory items, stock levels, or product details..."
    }
}

def log_message(assistant_id, level, message):
    """Add a log message to the session state logs for the specified assistant"""
    if assistant_id not in st.session_state.logs:
        st.session_state.logs[assistant_id] = []
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    log_entry = {
        "timestamp": timestamp,
        "level": level,
        "message": message
    }
    st.session_state.logs[assistant_id].append(log_entry)

def create_session_id(assistant_id):
    """Create a new session ID for the specified assistant"""
    session_id = str(uuid.uuid4())
    st.session_state.session_ids[assistant_id] = session_id
    st.session_state.chat_history[assistant_id] = []
    log_message(assistant_id, "INFO", f"Created new session with ID: {session_id}")
    return session_id

def send_message(assistant_id, message):
    """Send a message to the specified assistant and return the response"""
    assistant = assistants[assistant_id]
    session_id = st.session_state.session_ids.get(assistant_id)
    
    if not session_id:
        session_id = create_session_id(assistant_id)
    
    # Add user message to chat history
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.chat_history[assistant_id].append({
        "role": "user",
        "content": message,
        "timestamp": timestamp
    })
    
    # Prepare request payload
    message_history = [{"content": msg["content"], "sl_role": "USER" if msg["role"] == "user" else "ASSISTANT"} 
                       for msg in st.session_state.chat_history[assistant_id]]
    
    payload = [{"session_id": session_id, "messages": message_history}]
    
    log_message(assistant_id, "INFO", f"Sending request to {assistant['name']}")
    log_message(assistant_id, "INFO", f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Send request to API
        headers = {
            "Content-Type": "application/json",
            "Authorization": assistant["auth"]
        }
        
        start_time = time.time()
        response = requests.post(
            assistant["url"],
            headers=headers,
            json=payload
        )
        elapsed_time = time.time() - start_time
        
        log_message(assistant_id, "INFO", f"Response received in {elapsed_time:.2f} seconds")
        log_message(assistant_id, "INFO", f"Status code: {response.status_code}")
        
        # Process response
        if response.status_code == 200:
            try:
                response_data = response.json()
                log_message(assistant_id, "INFO", f"Response: {json.dumps(response_data, indent=2)}")
                
                # For different response formats
                if assistant_id in ["tomodachi", "zaiko"]:
                    # Format for tomodachi and zaiko
                    assistant_response = response_data.get("response", "")
                else:
                    # Format for shizoku
                    if isinstance(response_data, list) and len(response_data) > 0:
                        messages = response_data[0].get("messages", [])
                        # Get the last assistant message
                        assistant_messages = [msg["content"] for msg in messages if msg.get("sl_role") == "ASSISTANT"]
                        assistant_response = assistant_messages[-1] if assistant_messages else "No response from assistant"
                    else:
                        assistant_response = "Unexpected response format"
                
                # Add assistant response to chat history
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.chat_history[assistant_id].append({
                    "role": "assistant",
                    "content": assistant_response,
                    "timestamp": timestamp
                })
                
                return assistant_response
                
            except Exception as e:
                error_msg = f"Error parsing response: {str(e)}"
                log_message(assistant_id, "ERROR", error_msg)
                log_message(assistant_id, "ERROR", traceback.format_exc())
                return f"Error: {error_msg}"
        else:
            error_msg = f"Error: {response.status_code} - {response.text}"
            log_message(assistant_id, "ERROR", error_msg)
            return f"Error: Request failed with status code {response.status_code}"
            
    except Exception as e:
        error_msg = f"Exception occurred: {str(e)}"
        log_message(assistant_id, "ERROR", error_msg)
        log_message(assistant_id, "ERROR", traceback.format_exc())
        return f"Error: {error_msg}"

def display_chat_history(assistant_id):
    """Display the chat history for the specified assistant"""
    if assistant_id not in st.session_state.chat_history:
        return
    
    for message in st.session_state.chat_history[assistant_id]:
        message_type = "user" if message["role"] == "user" else "assistant"
        
        with st.container():
            st.markdown(f"""
            <div class="chat-message chat-message-{message_type}">
                <div class="chat-timestamp">{message["timestamp"]} | {message_type.capitalize()}</div>
                <div class="chat-message-content">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

def display_logs(assistant_id):
    """Display the logs for the specified assistant"""
    if assistant_id not in st.session_state.logs:
        return
    
    for log in st.session_state.logs[assistant_id]:
        log_class = "log-error" if log["level"] == "ERROR" else "log-info"
        
        st.markdown(f"""
        <div class="log-entry {log_class}">
            <span class="log-time">{log["timestamp"]} | {log["level"]}</span>
            <div>{log["message"]}</div>
        </div>
        """, unsafe_allow_html=True)

# Sidebar - Select assistant
with st.sidebar:
    st.title("Enterprise Assistant Hub")
    st.markdown("---")
    
    for assistant_id, assistant in assistants.items():
        if st.button(assistant["name"], key=f"select_{assistant_id}", use_container_width=True):
            st.session_state.current_assistant = assistant_id
            if assistant_id not in st.session_state.session_ids:
                create_session_id(assistant_id)
    
    st.markdown("---")
    st.caption("Enterprise Assistant Hub v1.0.0")
    st.caption("© 2025 Connect Faster Inc.")

# Main area - Chat interface
if st.session_state.current_assistant:
    assistant_id = st.session_state.current_assistant
    assistant = assistants[assistant_id]
    
    # Display assistant title and description
    st.markdown(f"""
    <div class="assistant-title">{assistant["name"]}</div>
    <div class="assistant-description">{assistant["description"]}</div>
    """, unsafe_allow_html=True)
    
    # Create tabs for chat and logs
    tab1, tab2 = st.tabs(["Chat", "Logs"])
    
    with tab1:
        # Display chat history
        chat_container = st.container()
        with chat_container:
            display_chat_history(assistant_id)
        
        # User input
        with st.container():
            user_input = st.text_input(
                "Your message",
                placeholder=assistant["placeholder"],
                key=f"input_{assistant_id}"
            )
            
            col1, col2 = st.columns([6, 1])
            with col2:
                if st.button("Send", key=f"send_{assistant_id}", use_container_width=True):
                    if user_input:
                        with st.spinner("Processing..."):
                            response = send_message(assistant_id, user_input)
                        st.experimental_rerun()
    
    with tab2:
        # Display logs
        logs_container = st.container()
        with logs_container:
            display_logs(assistant_id)
        
        if st.button("Clear Logs", key=f"clear_logs_{assistant_id}"):
            st.session_state.logs[assistant_id] = []
            log_message(assistant_id, "INFO", "Logs cleared")
            st.experimental_rerun()
else:
    # Welcome screen
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1 style="color: #90CDF4;">Welcome to Enterprise Assistant Hub</h1>
        <p style="color: #CBD5E0; font-size: 1.1rem; margin-bottom: 2rem;">
            Your centralized platform for intelligent business assistants
        </p>
        <div style="font-size: 5rem; margin-bottom: 2rem;">🤖</div>
        <p style="color: #A0AEC0;">
            Please select an assistant from the sidebar to begin.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    pass  # The app is already running through Streamlit
