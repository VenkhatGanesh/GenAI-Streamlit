import streamlit as st
import requests
import json
import uuid
import base64
from datetime import datetime
from io import BytesIO
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="Enterprise Assistant Hub",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for vibrant color scheme and styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #4361ee;
        --secondary-color: #3a0ca3;
        --accent-color: #7209b7;
        --background-color: #f8f9fa;
        --text-color: #212529;
        --success-color: #4cc9f0;
        --light-color: #f1faee;
    }
    
    /* General styling */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1lcbmhc {
        background-image: linear-gradient(to bottom, #4361ee, #3a0ca3);
    }
    
    .sidebar-link {
        display: block;
        padding: 15px;
        margin: 10px 0;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        color: white !important;
        text-align: center;
        text-decoration: none;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .sidebar-link:hover {
        transform: translateY(-2px);
        background-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    
    .sidebar-link.active {
        background-color: rgba(255, 255, 255, 0.3);
        border-left: 4px solid #f72585;
    }
    
    /* Chat container */
    .chat-container {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    
    /* Message styling */
    .user-message {
        background-color: #e9ecef;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 0;
        margin: 5px 0;
        display: inline-block;
        max-width: 80%;
    }
    
    .assistant-message {
        background-color: var(--primary-color);
        color: white;
        padding: 10px 15px;
        border-radius: 15px 15px 0 15px;
        margin: 5px 0;
        display: inline-block;
        max-width: 80%;
        float: right;
        clear: both;
    }
    
    /* Input box styling */
    .stTextInput input {
        border-radius: 20px;
        border: 1px solid #ced4da;
        padding: 10px 15px;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 20px;
        background-color: var(--primary-color);
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px 25px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: var(--secondary-color);
        transform: translateY(-2px);
    }
    
    /* Logo styling */
    .logo-container {
        text-align: center;
        margin-bottom: 20px;
    }
    
    .logo {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid white;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: var(--secondary-color);
        font-weight: bold;
    }
    
    /* Clear floats */
    .clearfix {
        clear: both;
    }
    
    /* Message container */
    .message-container {
        margin-bottom: 15px;
        overflow: hidden;
    }
    
    /* Timestamp styling */
    .timestamp {
        font-size: 0.7em;
        color: #6c757d;
        margin-top: 2px;
        text-align: right;
    }
    
    /* Message content */
    .message-content {
        overflow-wrap: break-word;
    }
    
    /* Code block styling */
    code {
        background-color: #f8f9fa;
        padding: 2px 4px;
        border-radius: 4px;
        color: #e83e8c;
    }
    
    pre {
        background-color: #212529;
        color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        overflow-x: auto;
    }
    
    /* Welcome message styling */
    .welcome-container {
        text-align: center;
        padding: 40px 20px;
        background-color: white;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
    }
    
    .welcome-image {
        max-width: 300px;
        margin: 20px auto;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Create or get session state variables
if 'current_assistant' not in st.session_state:
    st.session_state.current_assistant = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = {}
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Create assistant configurations
assistant_configs = {
    "shizoku": {
        "name": "Shizoku - The CRM Assistant",
        "url": "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/HRASSIST_agent_driver_VG_api",
        "auth": "Bearer z7gxfLKED6GRxY4Fdwcd9gcoWgJd5Q4c",
        "logo": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNTAgMjUwIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImEiIHgxPSIwIiB5MT0iMCIgeDI9IjEiIHkyPSIxIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjNDM2MWVlIi8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMWExODliIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PGNpcmNsZSBjeD0iMTI1IiBjeT0iMTI1IiByPSIxMjAiIGZpbGw9InVybCgjYSkiLz48cGF0aCBkPSJNODAgODBoOTB2OTBIODBWODBaIiBmaWxsPSJ3aGl0ZSIvPjxwYXRoIGQ9Ik05MCAxNDBoNzB2MzBIOTB2LTMwWiIgZmlsbD0id2hpdGUiLz48cGF0aCBkPSJNMTYwIDgwaDMwdjkwaC0zMFY4MFoiIGZpbGw9IndoaXRlIi8+PHRleHQgeD0iODAiIHk9IjE5MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjI0IiBmb250LXdlaWdodD0iYm9sZCIgZmlsbD0id2hpdGUiPlNoaXpva3U8L3RleHQ+PC9zdmc+",
        "welcome_image": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA1MDAgMzAwIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImEiIHgxPSIwIiB5MT0iMCIgeDI9IjEiIHkyPSIxIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjNDM2MWVlIi8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjM2EwY2EzIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHJlY3Qgd2lkdGg9IjUwMCIgaGVpZ2h0PSIzMDAiIGZpbGw9InVybCgjYSkiIHJ4PSIxNSIvPjxjaXJjbGUgY3g9IjI1MCIgY3k9IjEyMCIgcj0iNzAiIGZpbGw9IndoaXRlIi8+PGNpcmNsZSBjeD0iMjIwIiBjeT0iMTAwIiByPSIxMCIgZmlsbD0iIzIxMjUyOSIvPjxjaXJjbGUgY3g9IjI4MCIgY3k9IjEwMCIgcj0iMTAiIGZpbGw9IiMyMTI1MjkiLz48cGF0aCBkPSJNMjEwIDE1MGMzMCAzMCA1MCAzMCA4MCAwIiBzdHJva2U9IiMyMTI1MjkiIHN0cm9rZS13aWR0aD0iOCIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+PHRleHQgeD0iMjUwIiB5PSIyMzAiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIzMiIgZm9udC13ZWlnaHQ9ImJvbGQiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5IaSEgSeKAmW0gU2hpem9rdSE8L3RleHQ+PHRleHQgeD0iMjUwIiB5PSIyNjUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIyMCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiPllvdXIgQ1JNIEF1Z21lbnRhdGlvbiBBc3Npc3RhbnQ8L3RleHQ+PC9zdmc+",
        "welcome_message": "Welcome! I'm Shizoku, your CRM Assistant. I can help you access and analyze Salesforce CRM data, generate reports, and provide insights about your opportunities, contacts, and accounts. How can I assist you today?"
    },
    "tomodachi": {
        "name": "Tomodachi - HR Assistant",
        "url": "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/HRASSIST_agent_driver_VG_api",
        "auth": "Bearer 6BJ0xGbyAourBtiSgp7c2AZrvGvQ4eEd",
        "logo": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNTAgMjUwIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImEiIHgxPSIwIiB5MT0iMCIgeDI9IjEiIHkyPSIxIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjNzIwOWI3Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjM2EwY2EzIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PGNpcmNsZSBjeD0iMTI1IiBjeT0iMTI1IiByPSIxMjAiIGZpbGw9InVybCgjYSkiLz48Y2lyY2xlIGN4PSIxMjUiIGN5PSIxMDAiIHI9IjQwIiBmaWxsPSJ3aGl0ZSIvPjxwYXRoIGQ9Ik0xMjUgMTQwIGE1MCA1MCAwIDAgMCAtNTAgNTAgdjEwIGgxMDAgdi0xMCBhNTAgNTAgMCAwIDAgLTUwIC01MHoiIGZpbGw9IndoaXRlIi8+PHRleHQgeD0iODAiIHk9IjE5MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjI0IiBmb250LXdlaWdodD0iYm9sZCIgZmlsbD0id2hpdGUiPlRvbW9kYWNoaTwvdGV4dD48L3N2Zz4=",
        "welcome_image": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA1MDAgMzAwIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImEiIHgxPSIwIiB5MT0iMCIgeDI9IjEiIHkyPSIxIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjNzIwOWI3Ii8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjM2EwY2EzIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHJlY3Qgd2lkdGg9IjUwMCIgaGVpZ2h0PSIzMDAiIGZpbGw9InVybCgjYSkiIHJ4PSIxNSIvPjxjaXJjbGUgY3g9IjE3NSIgY3k9IjEyMCIgcj0iNTAiIGZpbGw9IndoaXRlIi8+PGNpcmNsZSBjeD0iMzI1IiBjeT0iMTIwIiByPSI1MCIgZmlsbD0id2hpdGUiLz48Y2lyY2xlIGN4PSIxNjAiIGN5PSIxMDUiIHI9IjgiIGZpbGw9IiMyMTI1MjkiLz48Y2lyY2xlIGN4PSIxOTAiIGN5PSIxMDUiIHI9IjgiIGZpbGw9IiMyMTI1MjkiLz48Y2lyY2xlIGN4PSIzMTAiIGN5PSIxMDUiIHI9IjgiIGZpbGw9IiMyMTI1MjkiLz48Y2lyY2xlIGN4PSIzNDAiIGN5PSIxMDUiIHI9IjgiIGZpbGw9IiMyMTI1MjkiLz48cGF0aCBkPSJNMTUwIDE0MGMxNSAyMCAzNSAyMCA1MCAwIiBzdHJva2U9IiMyMTI1MjkiIHN0cm9rZS13aWR0aD0iNiIgZmlsbD0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+PHBhdGggZD0iTTMwMCAxNDBjMTUgMjAgMzUgMjAgNTAgMCIgc3Ryb2tlPSIjMjEyNTI5IiBzdHJva2Utd2lkdGg9IjYiIGZpbGw9Im5vbmUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPjx0ZXh0IHg9IjI1MCIgeT0iMjMwIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMzIiIGZvbnQtd2VpZ2h0PSJib2xkIiBmaWxsPSJ3aGl0ZSIgdGV4dC1hbmNob3I9Im1pZGRsZSI+SGkhIFdl4oCZcmUgVG9tb2RhY2hpITwvdGV4dD48dGV4dCB4PSIyNTAiIHk9IjI2NSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjIwIiBmaWxsPSJ3aGl0ZSIgdGV4dC1hbmNob3I9Im1pZGRsZSI+WW91ciBIUiBBc3Npc3RhbnQgVGVhbTwvdGV4dD48L3N2Zz4=",
        "welcome_message": "Hello! We're Tomodachi, your HR Assistant team. We can help with HR policies, employee information, benefits, time-off requests, and other HR-related inquiries. How can we support you today?"
    },
    "zaiko": {
        "name": "Zaiko - The Inventory Manager",
        "url": "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/GadgetStore_agent_driver_VG_api",
        "auth": "Bearer JRJ5TFPwQMshJqxGVr0IQY5I5qYRGcDd",
        "logo": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNTAgMjUwIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImEiIHgxPSIwIiB5MT0iMCIgeDI9IjEiIHkyPSIxIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjNGNjOWYwIi8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMGY0YzVjIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PGNpcmNsZSBjeD0iMTI1IiBjeT0iMTI1IiByPSIxMjAiIGZpbGw9InVybCgjYSkiLz48cmVjdCB4PSI2MCIgeT0iOTAiIHdpZHRoPSIxMzAiIGhlaWdodD0iODAiIGZpbGw9IndoaXRlIiByeD0iNSIvPjxyZWN0IHg9IjgwIiB5PSI3MCIgd2lkdGg9IjkwIiBoZWlnaHQ9IjQwIiBmaWxsPSJ3aGl0ZSIgcng9IjUiLz48cmVjdCB4PSIxMDAiIHk9IjUwIiB3aWR0aD0iNTAiIGhlaWdodD0iNDAiIGZpbGw9IndoaXRlIiByeD0iNSIvPjxwYXRoIGQ9Ik03MCAxMDAgaDExMCBNOTAgODAgaDcwIE0xMTAgNjAgaDMwIiBzdHJva2U9IiMwZjRjNWMiIHN0cm9rZS13aWR0aD0iMiIgZmlsbD0ibm9uZSIvPjx0ZXh0IHg9IjgwIiB5PSIxOTAiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIyNCIgZm9udC13ZWlnaHQ9ImJvbGQiIGZpbGw9IndoaXRlIj5aYWlrbzwvdGV4dD48L3N2Zz4=",
        "welcome_image": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA1MDAgMzAwIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImEiIHgxPSIwIiB5MT0iMCIgeDI9IjEiIHkyPSIxIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjNGNjOWYwIi8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjMGY0YzVjIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHJlY3Qgd2lkdGg9IjUwMCIgaGVpZ2h0PSIzMDAiIGZpbGw9InVybCgjYSkiIHJ4PSIxNSIvPjxyZWN0IHg9IjEwMCIgeT0iNzAiIHdpZHRoPSIzMDAiIGhlaWdodD0iMTYwIiBmaWxsPSJ3aGl0ZSIgcng9IjEwIi8+PHJlY3QgeD0iMTIwIiB5PSI5MCIgd2lkdGg9IjI2MCIgaGVpZ2h0PSIxMjAiIGZpbGw9IiNmOGY5ZmEiIHJ4PSI1Ii8+PHJlY3QgeD0iMTQwIiB5PSIxMTAiIHdpZHRoPSI1MCIgaGVpZ2h0PSI4MCIgZmlsbD0iIzRjYzlmMCIgcng9IjUiLz48cmVjdCB4PSIyMDAiIHk9IjExMCIgd2lkdGg9IjUwIiBoZWlnaHQ9IjgwIiBmaWxsPSIjNGNjOWYwIiByeD0iNSIvPjxyZWN0IHg9IjI2MCIgeT0iMTEwIiB3aWR0aD0iNTAiIGhlaWdodD0iODAiIGZpbGw9IiM0Y2M5ZjAiIHJ4PSI1Ii8+PHJlY3QgeD0iMzIwIiB5PSIxMTAiIHdpZHRoPSI1MCIgaGVpZ2h0PSI4MCIgZmlsbD0iIzRjYzlmMCIgcng9IjUiLz48dGV4dCB4PSIyNTAiIHk9IjI2MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjI4IiBmb250LXdlaWdodD0iYm9sZCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiPkhpISBJJ20gWmFpa28sIFlvdXIgSW52ZW50b3J5IE1hbmFnZXI8L3RleHQ+PC9zdmc+",
        "welcome_message": "Hello! I'm Zaiko, your Inventory Manager. I can help you track gadget inventory, check stock levels, find product information, and manage inventory-related tasks. What would you like to know about our inventory today?"
    }
}

# Initialize history for each assistant if not present
for assistant_id in assistant_configs:
    if assistant_id not in st.session_state.conversation_history:
        st.session_state.conversation_history[assistant_id] = []

# Convert SVG data URI to image for display
def svg_to_image(svg_data):
    # Remove the data:image/svg+xml;base64, prefix
    svg_data = svg_data.split(",")[-1] if "," in svg_data else svg_data
    svg_bytes = base64.b64decode(svg_data)
    return Image.open(BytesIO(svg_bytes))

# Function to get current time
def get_current_time():
    return datetime.now().strftime("%H:%M")

# Function to send message to assistant API
def send_message_to_assistant(message, assistant_id):
    config = assistant_configs[assistant_id]
    
    # Prepare the conversation history for the API
    api_messages = []
    for msg in st.session_state.conversation_history[assistant_id]:
        api_messages.append({
            "content": msg["content"],
            "sl_role": "USER" if msg["role"] == "user" else "ASSISTANT"
        })
    
    # Add the new message
    api_messages.append({
        "content": message,
        "sl_role": "USER"
    })
    
    # Prepare the payload
    payload = json.dumps([{
        "session_id": st.session_state.session_id,
        "messages": api_messages
    }])
    
    # Set up headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": config["auth"]
    }
    
    try:
        # Make the API call
        response = requests.post(config["url"], headers=headers, data=payload)
        
        if response.status_code == 200:
            response_data = response.json()
            # For Shizoku and Zaiko, the response is structured differently
            if assistant_id == "shizoku" or assistant_id == "zaiko":
                return response_data.get("response", "Sorry, I couldn't process your request.")
            # For Tomodachi, the response structure is different
            elif assistant_id == "tomodachi":
                # Handle the response based on the Tomodachi format
                if isinstance(response_data, list) and len(response_data) > 0:
                    # Extract the messages from the response
                    messages = response_data[0].get("messages", [])
                    if messages and len(messages) > 0:
                        # Return the latest assistant message
                        latest_messages = [m.get("content", "") for m in messages if m.get("sl_role") == "ASSISTANT"]
                        if latest_messages:
                            return latest_messages[-1]
                return "Sorry, I couldn't process your request."
        else:
            return f"Error: {response.status_code}. Please try again later."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Function to handle sending messages
def handle_send():
    user_message = st.session_state.user_input
    if user_message:
        # Add user message to conversation history
        st.session_state.conversation_history[st.session_state.current_assistant].append({
            "role": "user",
            "content": user_message,
            "time": get_current_time()
        })
        
        # Clear input
        st.session_state.user_input = ""
        
        # Send message to assistant and get response
        assistant_response = send_message_to_assistant(user_message, st.session_state.current_assistant)
        
        # Add assistant response to conversation history
        st.session_state.conversation_history[st.session_state.current_assistant].append({
            "role": "assistant",
            "content": assistant_response,
            "time": get_current_time()
        })

# Main app layout
def main():
    # App title and header
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("https://raw.githubusercontent.com/streamlit/example-app-chatgpt-redesign/main/app/static/bot-head.png", width=80)
    with col2:
        st.title("Enterprise Assistant Hub")
        st.markdown("*Your all-in-one enterprise assistant platform*")
    
    # Create sidebar with navigation
    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>Assistant Directory</h2>", unsafe_allow_html=True)
        
        # Display logos for each assistant
        for assistant_id, config in assistant_configs.items():
            # Convert SVG to image
            logo_img = svg_to_image(config["logo"])
            
            # Create columns for logo and name
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(logo_img, width=50)
            with col2:
                # Create a button with the assistant's name
                if st.button(config["name"], key=f"btn_{assistant_id}"):
                    st.session_state.current_assistant = assistant_id
                    st.experimental_rerun()
        
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #6c757d;'>
                <p>© 2025 Enterprise Assistant Hub</p>
                <p style='font-size: 0.8em;'>Version 1.0.0</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Main content area
    if st.session_state.current_assistant is None:
        # Welcome screen when no assistant is selected
        st.markdown(
            """
            <div class="welcome-container">
                <h1>Welcome to Enterprise Assistant Hub</h1>
                <p style='font-size: 1.2em;'>Select an assistant from the sidebar to get started.</p>
                <img src="https://raw.githubusercontent.com/streamlit/example-app-chatgpt-redesign/main/app/static/bot-head.png" class="welcome-image">
                <p>Our specialized assistants are here to help with CRM, HR, and Inventory management tasks.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Get the current assistant config
        config = assistant_configs[st.session_state.current_assistant]
        
        # Display conversation
        st.markdown(f"<h2>{config['name']}</h2>", unsafe_allow_html=True)
        
        # Chat container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # If there's no conversation history for this assistant yet, show welcome message
        if len(st.session_state.conversation_history[st.session_state.current_assistant]) == 0:
            # Show welcome image
            welcome_img = svg_to_image(config["welcome_image"])
            st.image(welcome_img)
            
            # Add welcome message to conversation history
            st.session_state.conversation_history[st.session_state.current_assistant].append({
                "role": "assistant",
                "content": config["welcome_message"],
                "time": get_current_time()
            })
        
        # Display messages in conversation history
        for message in st.session_state.conversation_history[st.session_state.current_assistant]:
            if message["role"] == "user":
                st.markdown(
                    f"""
                    <div class="message-container">
                        <div class="user-message">
                            <div class="message-content">{message["content"]}</div>
                            <div class="timestamp">{message["time"]}</div>
                        </div>
                        <div class="clearfix"></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div class="message-container">
                        <div class="assistant-message">
                            <div class="message-content">{message["content"]}</div>
                            <div class="timestamp">{message["time"]}</div>
                        </div>
                        <div class="clearfix"></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Input area
        st.text_input(
            "Type your message",
            key="user_input",
            on_change=handle_send
        )
        
        # Information about the current assistant
        with st.expander("About this assistant"):
            st.markdown(
                f"""
                ### {config['name']}
                
                This assistant connects to enterprise systems to provide intelligent assistance for your business needs.
                
                **Features:**
                - Real-time data access
                - Conversational interface
                - Enterprise-grade security
                """
            )

# Run the app
if __name__ == "__main__":
    main()
