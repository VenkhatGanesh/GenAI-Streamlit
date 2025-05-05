import streamlit as st
import requests

# Function to call the API
def call_api(url, headers, payload):
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Sidebar with bot selection
st.sidebar.title("Select a Bot")
bot_selection = st.sidebar.radio("Choose a bot:", ("Shizoku-The CRM Assistant", "Tomodachi-HR Assistant", "Zaiko- The Inventory Manager"))

# Main app
st.title("Enterprise Grade Conversational Chatbot App")
st.markdown("Welcome to the enterprise-grade chatbot app. Select a bot from the sidebar to interact with.")

# Dark theme settings
st.markdown(
    """
    <style>
    .reportview-container {
        background: #2E2E2E;
        color: #FFFFFF;
    }
    .sidebar .sidebar-content {
        background: #1E1E1E;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Bot details
if bot_selection == "Shizoku-The CRM Assistant":
    st.header("Shizoku-The CRM Assistant")
    url = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/salesforce_agent_driver_VG_api"
    headers = {"Authorization": "Bearer z7gxfLKED6GRxY4Fdwcd9gcoWgJd5Q4c"}
    example_input = [{"session_id":"7474c028-cdd5-4ddf-adfd-96c8ddb38c9e","messages":[{"content":"select data from the opportunity object from salesforce","sl_role":"USER"}]}]
    st.json(example_input)
    if st.button("Send Request"):
        response = call_api(url, headers, example_input)
        st.json(response)

elif bot_selection == "Tomodachi-HR Assistant":
    st.header("Tomodachi-HR Assistant")
    url = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/HRASSIST_agent_driver_VG_api"
    headers = {"Authorization": "Bearer 6BJ0xGbyAourBtiSgp7c2AZrvGvQ4eEd"}
    example_input = [{"session_id":"7474c028-cdd5-4ddf-adfd-96c8ddb38c9e","messages":[{"content":"Who should we reach in case of fire emergency and send me the info over email?","sl_role":"USER"}]}]
    st.json(example_input)
    if st.button("Send Request"):
        response = call_api(url, headers, example_input)
        st.json(response)

elif bot_selection == "Zaiko- The Inventory Manager":
    st.header("Zaiko- The Inventory Manager")
    url = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/GadgetStore_agent_driver_VG_api"
    headers = {"Authorization": "Bearer JRJ5TFPwQMshJqxGVr0IQY5I5qYRGcDd"}
    example_input = [{"session_id":"7474c028-cdd5-4ddf-adfd-96c8ddb38c9e","messages":[{"content":"Get All items in the gadget inventory","sl_role":"USER"}]}]
    st.json(example_input)
    if st.button("Send Request"):
        response = call_api(url, headers, example_input)
        st.json(response)

# Display logs
st.sidebar.title("Logs")
st.sidebar.text("Logs will be displayed here.")
