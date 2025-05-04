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
        "api_key": "Bearer 6BJ
