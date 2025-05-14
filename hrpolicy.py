import streamlit as st
import requests
import uuid
import json

# Set page configuration
st.set_page_config(
    page_title="New Horizon Public School HR Policy Assistant",
    page_icon="🏫",
    layout="centered"
)

# API Details
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/HR_Policy_Driver_api"
API_KEY = "Bearer 3RslysNL8upsL7Hp6ownhZJMJFwzvdJm"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Function to call the HR Policy API
def query_hr_policy_api(user_message):
    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = [{
        "session_id": st.session_state.session_id,
        "messages": [{
            "content": user_message,
            "sl_role": "USER"
        }]
    }]
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return {"response": "I'm sorry, there was an error connecting to the HR policy database. Please try again later."}

# App header
st.title("New Horizon Public School")
st.subheader("HR Policy Assistant")
st.markdown("""
    Welcome to the HR Policy Assistant! I can help answer your questions about New Horizon Public School's HR policies.
    Ask me anything about:
    - Leave policies
    - Benefits
    - Induction procedures
    - Performance reviews
    - And more!
""")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
user_query = st.chat_input("Ask about an HR policy...")

# Process user input
if user_query:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_query)
    
    # Display assistant response with a spinner while waiting
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Query the HR Policy API
            response_data = query_hr_policy_api(user_query)
            assistant_response = response_data.get("response", "I'm sorry, I couldn't retrieve an answer at this time.")
            
            # Display the response
            st.markdown(assistant_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})

# Add sidebar with information
with st.sidebar:
    st.header("About")
    st.markdown("""
        This HR Policy Assistant uses New Horizon Public School's official HR policies to provide accurate information to staff members.
        
        Your conversations are private and secure.
    """)
    
    # Add reset button
    if st.button("Start New Conversation"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
