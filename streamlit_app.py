import streamlit as st
import requests
import uuid
import json
import base64
from datetime import datetime
import re

# Set page configuration
st.set_page_config(
    page_title="Enterprise Assistant Hub",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define some vibrant colors
PRIMARY_COLOR = "#4361EE"
SECONDARY_COLOR = "#3A0CA3"
ACCENT_COLOR_1 = "#7209B7"
ACCENT_COLOR_2 = "#F72585"
ACCENT_COLOR_3 = "#4CC9F0"
BG_COLOR = "#F8F9FA"
TEXT_COLOR = "#212529"

# Apply custom CSS
st.markdown(f"""
<style>
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}
    .stTextInput, .stTextArea {{
        background-color: {BG_COLOR};
    }}
    .stButton>button {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }}
    .stButton>button:hover {{
        background-color: {SECONDARY_COLOR};
    }}
    .chat-message {{
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: row;
        align-items: flex-start;
    }}
    .chat-message.user {{
        background-color: #E9ECEF;
        color: {TEXT_COLOR};
    }}
    .chat-message.assistant {{
        background-color: #D8E2DC;
        color: {TEXT_COLOR};
    }}
    .chat-message .avatar {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }}
    .chat-message .message {{
        flex-grow: 1;
    }}
    .logo-header {{
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
    }}
    .logo-header img {{
        height: 64px;
        width: 64px;
    }}
    .logo-header h1 {{
        margin: 0;
        color: {PRIMARY_COLOR};
    }}
    .sidebar-logo {{
        width: 32px;
        height: 32px;
        margin-right: 0.5rem;
        vertical-align: middle;
    }}
    .sidebar-header {{
        margin-bottom: 2rem;
        text-align: center;
    }}
    .sidebar-header img {{
        width: 150px;
        height: auto;
        margin-bottom: 1rem;
    }}
    code {{
        white-space: pre-wrap !important;
    }}
    .json-block {{
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 5px;
        overflow-x: auto;
        margin: 1rem 0;
    }}
    .session-status {{
        font-size: 0.8rem;
        color: #6c757d;
        margin-top: 0.5rem;
    }}
    .stMarkdown {{
        overflow-wrap: break-word;
    }}
</style>
""", unsafe_allow_html=True)

# Logo SVG data in base64
def get_logo_b64(logo_name):
    if logo_name == "hub":
        return "https://img.icons8.com/fluency/96/hub.png"
    elif logo_name == "crm":
        return "https://img.icons8.com/fluency/96/customer-relationship-management.png"
    elif logo_name == "hr":
        return "https://img.icons8.com/fluency/96/human-resources.png"
    elif logo_name == "inventory":
        return "https://img.icons8.com/fluency/96/inventory.png"
    elif logo_name == "greeting":
        return "https://img.icons8.com/fluency/96/chat.png"
    
    # Default case - should never happen
    return "https://img.icons8.com/fluency/96/artificial-intelligence.png"

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
        "logo": get_logo_b64("hub"),
        "color": PRIMARY_COLOR,
        "welcome_message": "👋 Welcome to the Enterprise Assistant Hub! Please select an assistant from the sidebar to get started.",
    },
    "crm": {
        "name": "Shizoku - The CRM Assistant",
        "logo": get_logo_b64("crm"),
        "color": ACCENT_COLOR_1,
        "api_url": "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/HRASSIST_agent_driver_VG_api",
        "api_key": "Bearer z7gxfLKED6GRxY4Fdwcd9gcoWgJd5Q4c",
        "welcome_message": "👋 Hello! I'm Shizoku, your CRM Assistant. I can help you retrieve and analyze data from your Salesforce opportunities. How can I assist you today?",
        "greeting_image": get_logo_b64("greeting")
    },
    "hr": {
        "name": "Tomodachi - HR Assistant",
        "logo": get_logo_b64("hr"),
        "color": ACCENT_COLOR_2,
        "api_url": "",  # URL not provided in the specifications
        "api_key": "Bearer 6BJ0xGbyAourBtiSgp7c2AZrvGvQ4eEd",
        "welcome_message": "👋 Hi there! I'm Tomodachi, your HR Assistant. I can help you with HR-related inquiries, employee information, and emergency contacts. How can I help you today?",
        "greeting_image": get_logo_b64("greeting")
    },
    "inventory": {
        "name": "Zaiko - The Inventory Manager",
        "logo": get_logo_b64("inventory"),
        "color": ACCENT_COLOR_3,
        "api_url": "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/GadgetStore_agent_driver_VG_api",
        "api_key": "Bearer JRJ5TFPwQMshJqxGVr0IQY5I5qYRGcDd",
        "welcome_message": "👋 Greetings! I'm Zaiko, your Inventory Manager. I can help you manage and query your gadget inventory. What would you like to know about your inventory today?",
        "greeting_image": get_logo_b64("greeting")
    }
}

# Display main logo and title
def display_header():
    assistant = assistant_config[st.session_state.current_assistant]
    st.markdown(
        f"""
        <div class="logo-header">
            <img src="{assistant['logo']}" alt="{assistant['name']} Logo">
            <h1>{assistant['name']}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

# Sidebar navigation
def sidebar():
    with st.sidebar:
        st.title("Enterprise AI Assistants")
        st.image("https://assets.snaplogic.com/logo/snaplogic-RGB-3color.png", width=200)

        # Assistant selection
        st.markdown("### Choose your Assistant")
        
        # Display assistant buttons without HTML in them
        col1, col2, col3 = st.columns([0.2, 0.8, 0.2])
        
        # CRM Assistant Button section
        with col1:
            st.image(assistant_config['crm']['logo'], width=30)
        with col2:
            if st.button(
                "Shizoku - The CRM Assistant",
                key="crm_button",
                use_container_width=True,
                help="Access your CRM assistant",
                type="primary" if st.session_state.current_assistant == "crm" else "secondary"
            ):
                st.session_state.current_assistant = "crm"
                reset_conversation(add_welcome=True)
                st.rerun()
        with col3:
            st.write("")  # Empty column for spacing
            
        # HR Assistant Button section
        with col1:
            st.image(assistant_config['hr']['logo'], width=30)
        with col2:
            if st.button(
                "Tomodachi - HR Assistant",
                key="hr_button",
                use_container_width=True,
                help="Access your HR assistant",
                type="primary" if st.session_state.current_assistant == "hr" else "secondary"
            ):
                st.session_state.current_assistant = "hr"
                reset_conversation(add_welcome=True)
                st.rerun()
        with col3:
            st.write("")  # Empty column for spacing
            
        # Inventory Assistant Button section
        with col1:
            st.image(assistant_config['inventory']['logo'], width=30)
        with col2:
            if st.button(
                "Zaiko - The Inventory Manager",
                key="inventory_button",
                use_container_width=True,
                help="Access your inventory management assistant",
                type="primary" if st.session_state.current_assistant == "inventory" else "secondary"
            ):
            st.session_state.current_assistant = "inventory"
            reset_conversation(add_welcome=True)
            st.rerun()

        # Display session information
        st.markdown(
            f"""
            <div class="session-status">
                <strong>Session ID:</strong> {st.session_state.session_id[:8]}...<br>
                <strong>Started:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Reset conversation button
        if st.button("🔄 Reset Conversation", use_container_width=True):
            reset_conversation(add_welcome=True)
            st.rerun()

def reset_conversation(add_welcome=False):
    st.session_state.messages = []
    if add_welcome and st.session_state.current_assistant != "hub":
        assistant = assistant_config[st.session_state.current_assistant]
        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant["welcome_message"],
            "image": assistant["greeting_image"]
        })

# Format messages for API
def format_messages_for_api(messages):
    formatted_messages = []
    for message in messages:
        if message["role"] == "user":
            formatted_messages.append({
                "content": message["content"],
                "sl_role": "USER"
            })
        elif message["role"] == "assistant":
            # Skip assistant messages with images as they're just welcome messages
            if "image" not in message:
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

# Function to display chat messages
def display_chat():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "image" in message:
                st.markdown(f'<img src="{message["image"]}" width="100">', unsafe_allow_html=True)
            
            # Process code blocks in the message
            content = message["content"]
            
            # Parse markdown code blocks and JSON blocks for better formatting
            if "```json" in content or "```" in content:
                parts = re.split(r'(```(?:json)?\n[\s\S]*?\n```)', content)
                for part in parts:
                    if part.startswith("```json\n") or part.startswith("```\n"):
                        # Extract the code content
                        code_content = part.split("```")[1].strip()
                        if code_content.startswith("json\n"):
                            code_content = code_content[5:]
                        
                        # Try to format JSON nicely if it's valid JSON
                        try:
                            if code_content.strip().startswith("[") or code_content.strip().startswith("{"):
                                parsed_json = json.loads(code_content)
                                st.json(parsed_json)
                            else:
                                st.code(code_content)
                        except:
                            st.code(code_content)
                    else:
                        if part.strip():
                            st.markdown(part)
            else:
                st.markdown(content)

# Chat interface
def main():
    display_header()
    sidebar()
    
    if st.session_state.current_assistant == "hub":
        # Display welcome message for hub
        st.markdown(f"# Welcome to Enterprise Assistant Hub")
        st.markdown("""
        This platform provides you with specialized AI assistants to help with different aspects of your enterprise operations.
        
        Please select an assistant from the sidebar to get started:
        
        - **Shizoku** - Your CRM Assistant for managing customer relationships
        - **Tomodachi** - Your HR Assistant for human resources inquiries
        - **Zaiko** - Your Inventory Manager for tracking and managing inventory
        
        Each assistant is specialized in its domain and can help you retrieve information, analyze data, and perform tasks.
        """)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.image(assistant_config['crm']['logo'], width=64)
            st.subheader("Shizoku")
            st.write("CRM Assistant for Salesforce data")
        
        with col2:
            st.image(assistant_config['hr']['logo'], width=64)
            st.subheader("Tomodachi")
            st.write("HR Assistant for employee information")
        
        with col3:
            st.image(assistant_config['inventory']['logo'], width=64)
            st.subheader("Zaiko")
            st.write("Inventory Manager for gadget tracking")
        
    else:
        # Display the chat interface
        display_chat()
        
        # Handle user input
        user_input = st.chat_input("Type your message here...")
        if user_input:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Show thinking status
            with st.status("Thinking...", expanded=True):
                st.write("Connecting to assistant API...")
                
                # Call API
                response_data = call_assistant_api(st.session_state.messages[-1]["content"])
                
                if "response" in response_data:
                    # Add assistant response to chat
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response_data["response"]
                    })
                else:
                    # Handle error
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": "I'm sorry, I couldn't process your request. Please try again."
                    })
            
            # Rerun to update the UI with the new message
            st.rerun()
        
        # Process last user message if it hasn't been responded to
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            with st.status("Thinking...", expanded=True):
                st.write("Connecting to assistant API...")
                
                # Call API
                response_data = call_assistant_api(st.session_state.messages[-1]["content"])
                
                if "response" in response_data:
                    # Add assistant response to chat
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response_data["response"]
                    })
                    st.rerun()
                else:
                    # Handle error
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": "I'm sorry, I couldn't process your request. Please try again."
                    })
                    st.rerun()

# Run the app
if __name__ == "__main__":
    main()
