import streamlit as st
import requests
import uuid
import json
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="Enterprise Assistant Hub",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply dark theme styling
def apply_custom_style():
    st.markdown("""
    <style>
    .main {
        background-color: #1E1E1E;
        color: #E0E0E0;
    }
    .stTextInput>div>div>input {
        background-color: #2D2D2D;
        color: #E0E0E0;
    }
    .stButton>button {
        background-color: #0078D7;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #005A9E;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #2B5A89;
        border-right: 5px solid #0078D7;
    }
    .chat-message.assistant {
        background-color: #3A3A3A;
        border-left: 5px solid #777777;
    }
    .chat-message .message-content {
        display: flex;
        margin-left: 10px;
        padding-left: 10px;
    }
    .log-panel {
        background-color: #2D2D2D;
        padding: 10px;
        border-radius: 5px;
        max-height: 200px;
        overflow-y: auto;
        margin-top: 10px;
        font-family: monospace;
        color: #00FF00;
    }
    .log-entry {
        margin-bottom: 5px;
        border-bottom: 1px solid #444;
        padding-bottom: 3px;
    }
    .log-timestamp {
        color: #888;
        font-size: 0.85em;
    }
    .log-message {
        margin-left: 10px;
    }
    .selected-bot {
        background-color: #0078D7 !important;
        color: white !important;
        padding: 10px !important;
        border-radius: 5px !important;
        margin-bottom: 10px !important;
    }
    div[data-testid="stSidebarNav"] li div a {
        margin-bottom: 10px;
        padding: 10px;
        border-radius: 5px;
        background-color: #2D2D2D;
        color: #E0E0E0;
        transition: all 0.3s;
    }
    div[data-testid="stSidebarNav"] li div a:hover {
        background-color: #3D3D3D;
    }
    .stTextArea textarea {
        background-color: #2D2D2D;
        color: #E0E0E0;
    }
    </style>
    """, unsafe_allow_html=True)

apply_custom_style()

# Bot configuration
bot_configs = {
    "Shizoku-The CRM Assistant": {
        "url": "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/salesforce_agent_driver_VG_api",
        "auth": "Bearer z7gxfLKED6GRxY4Fdwcd9gcoWgJd5Q4c",
        "icon": "💼",
        "color": "#4285F4",
        "description": "Your Salesforce CRM expert. Ask about customers, opportunities, and sales data."
    },
    "Tomodachi-HR Assistant": {
        "url": "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/HRASSIST_agent_driver_VG_api",
        "auth": "Bearer 6BJ0xGbyAourBtiSgp7c2AZrvGvQ4eEd",
        "icon": "👥",
        "color": "#EA4335",
        "description": "Your HR support specialist. Get information about policies, employees, and HR processes."
    },
    "Zaiko-The Inventory Manager": {
        "url": "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/GadgetStore_agent_driver_VG_api",
        "auth": "Bearer JRJ5TFPwQMshJqxGVr0IQY5I5qYRGcDd",
        "icon": "📦",
        "color": "#34A853",
        "description": "Your inventory expert. Lookup product details, check stock levels, and manage inventory."
    }
}

# Initialize session state variables
if 'current_bot' not in st.session_state:
    st.session_state.current_bot = "Shizoku-The CRM Assistant"

if 'session_ids' not in st.session_state:
    st.session_state.session_ids = {bot: str(uuid.uuid4()) for bot in bot_configs}

if 'conversations' not in st.session_state:
    st.session_state.conversations = {bot: [] for bot in bot_configs}

if 'logs' not in st.session_state:
    st.session_state.logs = {bot: [] for bot in bot_configs}

# Function to add log entries
def add_log(bot_name, message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    log_entry = {
        "timestamp": timestamp,
        "level": level,
        "message": message
    }
    st.session_state.logs[bot_name].append(log_entry)
    # Keep only the last 100 log entries
    if len(st.session_state.logs[bot_name]) > 100:
        st.session_state.logs[bot_name] = st.session_state.logs[bot_name][-100:]

# Function to send message to bot API
def send_message(bot_name, user_message):
    bot_config = bot_configs[bot_name]
    session_id = st.session_state.session_ids[bot_name]
    
    # Add user message to conversation
    st.session_state.conversations[bot_name].append({"role": "user", "content": user_message})
    
    # Prepare conversation history for API
    conversation_for_api = [
        {"content": msg["content"], "sl_role": "USER" if msg["role"] == "user" else "ASSISTANT"}
        for msg in st.session_state.conversations[bot_name]
    ]
    
    # Prepare API payload
    payload = [{"session_id": session_id, "messages": conversation_for_api}]
    
    # Log API request
    add_log(bot_name, f"API Request: {json.dumps(payload)}", "DEBUG")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": bot_config["auth"]
    }
    
    try:
        add_log(bot_name, f"Sending request to {bot_config['url']}", "INFO")
        start_time = time.time()
        
        response = requests.post(
            bot_config["url"],
            headers=headers,
            data=json.dumps(payload),
            timeout=30  # 30 seconds timeout
        )
        
        elapsed_time = time.time() - start_time
        add_log(bot_name, f"Response received in {elapsed_time:.2f}s", "INFO")
        
        if response.status_code == 200:
            add_log(bot_name, f"API Success: {response.status_code}", "INFO")
            
            try:
                response_data = response.json()
                add_log(bot_name, f"Response data: {json.dumps(response_data)}", "DEBUG")
                
                # Handle different response formats
                bot_response = ""
                if isinstance(response_data, list):
                    # Format for Shizoku
                    for msg in response_data[0]["messages"]:
                        if msg["sl_role"] == "ASSISTANT" and msg["content"] not in [m["content"] for m in st.session_state.conversations[bot_name] if m["role"] == "assistant"]:
                            bot_response = msg["content"]
                elif isinstance(response_data, dict) and "response" in response_data:
                    # Format for Tomodachi and Zaiko
                    bot_response = response_data["response"]
                
                if bot_response:
                    # Add assistant response to conversation
                    st.session_state.conversations[bot_name].append({"role": "assistant", "content": bot_response})
                    return bot_response
                else:
                    error_msg = "Could not parse response from API."
                    add_log(bot_name, error_msg, "ERROR")
                    return error_msg
                
            except Exception as e:
                error_msg = f"Error parsing response: {str(e)}"
                add_log(bot_name, error_msg, "ERROR")
                return error_msg
                
        else:
            error_msg = f"API Error: {response.status_code} - {response.text}"
            add_log(bot_name, error_msg, "ERROR")
            return f"Sorry, I encountered an error: HTTP {response.status_code}. Please try again later."
            
    except requests.exceptions.Timeout:
        error_msg = "Request timed out after 30 seconds."
        add_log(bot_name, error_msg, "ERROR")
        return "Sorry, the request timed out. Please try again later."
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Request error: {str(e)}"
        add_log(bot_name, error_msg, "ERROR")
        return f"Sorry, there was an error communicating with the service: {str(e)}"

# Sidebar
with st.sidebar:
    st.title("Enterprise Assistant Hub")
    st.markdown("---")
    
    # Bot selection
    st.subheader("Select your assistant")
    
    for bot_name in bot_configs:
        icon = bot_configs[bot_name]["icon"]
        if st.button(f"{icon} {bot_name}", key=f"btn_{bot_name}", 
                    help=bot_configs[bot_name]["description"],
                    use_container_width=True,
                    type="primary" if bot_name == st.session_state.current_bot else "secondary"):
            st.session_state.current_bot = bot_name
            st.rerun()
    
    st.markdown("---")
    st.subheader("Current Session Info")
    st.caption(f"Bot: {st.session_state.current_bot}")
    st.caption(f"Session ID: {st.session_state.session_ids[st.session_state.current_bot]}")
    
    # New conversation button
    if st.button("Start New Conversation", use_container_width=True):
        st.session_state.session_ids[st.session_state.current_bot] = str(uuid.uuid4())
        st.session_state.conversations[st.session_state.current_bot] = []
        st.session_state.logs[st.session_state.current_bot] = []
        add_log(st.session_state.current_bot, "New conversation started", "INFO")
        st.rerun()

# Main area
current_bot = st.session_state.current_bot
bot_config = bot_configs[current_bot]

# Header
st.markdown(f"<h1 style='color:{bot_config['color']};'>{bot_config['icon']} {current_bot}</h1>", unsafe_allow_html=True)
st.markdown(f"<p>{bot_config['description']}</p>", unsafe_allow_html=True)
st.markdown("---")

# Display conversation
for message in st.session_state.conversations[current_bot]:
    if message["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant", avatar=bot_config["icon"]):
            st.write(message["content"])

# User input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Process user input
    with st.chat_message("user", avatar="👤"):
        st.write(user_input)
    
    with st.spinner(f"{bot_config['icon']} Processing..."):
        add_log(current_bot, f"User message: {user_input}", "INFO")
        bot_response = send_message(current_bot, user_input)
    
    with st.chat_message("assistant", avatar=bot_config["icon"]):
        st.write(bot_response)

# Advanced section with collapsible logs
with st.expander("System Logs", expanded=False):
    if st.button("Clear Logs"):
        st.session_state.logs[current_bot] = []
        add_log(current_bot, "Logs cleared", "INFO")
        st.rerun()
    
    st.markdown("<div class='log-panel'>", unsafe_allow_html=True)
    
    for log in reversed(st.session_state.logs[current_bot]):
        level_color = {
            "INFO": "#00FF00", 
            "DEBUG": "#FFFF00", 
            "ERROR": "#FF0000", 
            "WARNING": "#FFA500"
        }.get(log["level"], "#FFFFFF")
        
        st.markdown(
            f"<div class='log-entry'>"
            f"<span class='log-timestamp'>{log['timestamp']}</span> "
            f"<span style='color:{level_color};'>[{log['level']}]</span>"
            f"<span class='log-message'>{log['message']}</span>"
            f"</div>", 
            unsafe_allow_html=True
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
