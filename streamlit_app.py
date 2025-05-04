import streamlit as st
import requests
import uuid
import json
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Enterprise Assistant Hub",
    page_icon="🤖",
    layout="wide",
)

# Define some colors
PRIMARY_COLOR = "#4361EE"
SECONDARY_COLOR = "#3A0CA3"
ACCENT_COLOR_1 = "#7209B7"
ACCENT_COLOR_2 = "#F72585"
ACCENT_COLOR_3 = "#4CC9F0"

# Initialize session state
if 'current_assistant' not in st.session_state:
    st.session_state.current_assistant = "hub"
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Define assistant configurations
assistant_config = {
    "hub": {
        "name": "Enterprise Assistant Hub",
        "logo": "https://img.icons8.com/fluency/96/hub.png",
        "color": PRIMARY_COLOR,
        "welcome_message": "👋 Welcome to the Enterprise Assistant Hub! Please select an assistant from the sidebar to get started.",
    },
    "crm": {
        "name": "Shizoku - The CRM Assistant",
        "logo": "https://img.icons8.com/fluency/96/customer-relationship-management.png",
        "color": ACCENT_COLOR_1,
        "api_url": "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/HRASSIST_agent_driver_VG_api",
        "api_key": "Bearer z7gxfLKED6GRxY4Fdwcd9gcoWgJd5Q4c",
        "welcome_message": "👋 Hello! I'm Shizoku, your CRM Assistant. I can help you retrieve and analyze data from your Salesforce opportunities. How can I assist you today?",
        "greeting_image": "https://img.icons8.com/fluency/96/chat.png"
    },
    "hr": {
        "name": "Tomodachi - HR Assistant",
        "logo": "https://img.icons8.com/fluency/96/human-resources.png",
        "color": ACCENT_COLOR_2,
        "api_url": "",  # URL not provided in the specifications
        "api_key": "Bearer 6BJ0xGbyAourBtiSgp7c2AZrvGvQ4eEd",
        "welcome_message": "👋 Hi there! I'm Tomodachi, your HR Assistant. I can help you with HR-related inquiries, employee information, and emergency contacts. How can I help you today?",
        "greeting_image": "https://img.icons8.com/fluency/96/chat.png"
    },
    "inventory": {
        "name": "Zaiko - The Inventory Manager",
        "logo": "https://img.icons8.com/fluency/96/inventory.png",
        "color": ACCENT_COLOR_3,
        "api_url": "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/GadgetStore_agent_driver_VG_api",
        "api_key": "Bearer JRJ5TFPwQMshJqxGVr0IQY5I5qYRGcDd",
        "welcome_message": "👋 Greetings! I'm Zaiko, your Inventory Manager. I can help you manage and query your gadget inventory. What would you like to know about your inventory today?",
        "greeting_image": "https://img.icons8.com/fluency/96/chat.png"
    }
}

# Sidebar navigation
with st.sidebar:
    st.title("Enterprise AI Assistants")
    st.image("https://assets.snaplogic.com/logo/snaplogic-RGB-3color.png", width=200)
    
    st.markdown("### Choose your Assistant")
    
    # CRM Assistant
    if st.button("Shizoku - CRM Assistant", key="crm_btn", use_container_width=True):
        st.session_state.current_assistant = "crm"
        st.session_state.messages = []
        # Add welcome message
        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_config["crm"]["welcome_message"],
            "image": assistant_config["crm"]["greeting_image"]
        })
        st.rerun()
    
    # HR Assistant
    if st.button("Tomodachi - HR Assistant", key="hr_btn", use_container_width=True):
        st.session_state.current_assistant = "hr"
        st.session_state.messages = []
        # Add welcome message
        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_config["hr"]["welcome_message"],
            "image": assistant_config["hr"]["greeting_image"]
        })
        st.rerun()
    
    # Inventory Assistant
    if st.button("Zaiko - Inventory Manager", key="inv_btn", use_container_width=True):
        st.session_state.current_assistant = "inventory"
        st.session_state.messages = []
        # Add welcome message
        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_config["inventory"]["welcome_message"],
            "image": assistant_config["inventory"]["greeting_image"]
        })
        st.rerun()
    
    # Display session information
    st.markdown("---")
    st.caption(f"Session ID: {st.session_state.session_id[:8]}...")
    st.caption(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Reset conversation button
    if st.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state.messages = []
        if st.session_state.current_assistant != "hub":
            # Add welcome message
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_config[st.session_state.current_assistant]["welcome_message"],
                "image": assistant_config[st.session_state.current_assistant]["greeting_image"]
            })
        st.rerun()

# Format messages for API
def format_messages_for_api(messages):
    formatted_messages = []
    for message in messages:
        if message["role"] == "user":
            formatted_messages.append({
                "content": message["content"],
                "sl_role": "USER"
            })
        elif message["role"] == "assistant" and "image" not in message:
            formatted_messages.append({
                "content": message["content"],
                "sl_role": "ASSISTANT"
            })
    return formatted_messages

# Function to call the API
def call_assistant_api(user_input):
    assistant_key = st.session_state.current_assistant
    assistant = assistant_config[assistant_key]
    
    if not assistant.get("api_url"):
        # If no API URL is provided, simulate a response for demo purposes
        return {
            "response": f"This is a simulated response for {assistant['name']}. In a production environment, this would connect to the API endpoint. Your message was: {user_input}"
        }
    
    # Format the payload
    payload = [{
        "session_id": st.session_state.session_id,
        "messages": format_messages_for_api(st.session_state.messages)
    }]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": assistant["api_key"]
    }
    
    try:
        response = requests.post(
            assistant["api_url"],
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "response": f"Error: Received status code {response.status_code} from the API. Please try again later."
            }
    except Exception as e:
        return {
            "response": f"Error: Could not connect to the API. {str(e)}"
        }

# Main content display
current = st.session_state.current_assistant
assistant = assistant_config[current]

# Display the assistant name and logo
st.title(assistant["name"])
col1, col2 = st.columns([1, 5])
with col1:
    st.image(assistant["logo"], width=64)

# Hub welcome screen
if current == "hub":
    st.write("""
    This platform provides you with specialized AI assistants to help with different aspects of your enterprise operations.
    
    Please select an assistant from the sidebar to get started:
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.image(assistant_config["crm"]["logo"], width=64)
        st.subheader("Shizoku")
        st.write("CRM Assistant for Salesforce data")
    
    with col2:
        st.image(assistant_config["hr"]["logo"], width=64)
        st.subheader("Tomodachi")
        st.write("HR Assistant for employee information")
    
    with col3:
        st.image(assistant_config["inventory"]["logo"], width=64)
        st.subheader("Zaiko")
        st.write("Inventory Manager for gadget tracking")

# Chat interface
else:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "image" in message:
                st.image(message["image"], width=100)
            st.write(message["content"])
    
    # Get user input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()
    
    # Process the last user message if it hasn't been responded to
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.status("Processing your request...", expanded=True):
            st.write("Connecting to assistant API...")
            
            # Call API
            response_data = call_assistant_api(st.session_state.messages[-1]["content"])
            
            # Add response to chat
            if "response" in response_data:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_data["response"]
                })
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "I'm sorry, I couldn't process your request. Please try again."
                })
        
        st.rerun()
