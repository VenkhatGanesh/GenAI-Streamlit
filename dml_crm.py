import streamlit as st
import requests
import uuid
import json
from datetime import datetime
import base64

# Set page configuration
st.set_page_config(
    page_title="Schneider Electric Assistant",
    page_icon="⚡",
    layout="wide"
)

# Define Schneider Electric brand colors
PRIMARY_COLOR = "#3DCD58"  # Schneider Green
SECONDARY_COLOR = "#2C2E35"  # Dark Gray
ACCENT_COLOR = "#009530"  # Darker Green
BG_COLOR = "#E8F5E9"  # Light Green Background
TEXT_COLOR = "#1D252D"  # Dark Text

# CSS for styling
def local_css():
    st.markdown("""
    <style>
        /* Main styling */
        .stApp {
            background-color: #E8F5E9;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #009530;
            font-family: 'Roboto', sans-serif;
            font-weight: 600;
        }
        
        /* Text elements */
        p, li, div {
            color: #1D252D;
            font-family: 'Open Sans', sans-serif;
        }
        
        /* Buttons */
        .stButton button {
            background-color: #3DCD58;
            color: white;
            border-radius: 4px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .stButton button:hover {
            background-color: #009530;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        /* Chat container */
        .chat-container {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        
        /* User message */
        .user-message {
            background-color: #E5F5E8;
            border-radius: 15px 15px 0 15px;
            padding: 10px 15px;
            margin: 5px 0;
            max-width: 80%;
            align-self: flex-end;
            margin-left: auto;
        }
        
        /* Bot message */
        .bot-message {
            background-color: #F0F2F5;
            border-radius: 15px 15px 15px 0;
            padding: 10px 15px;
            margin: 5px 0;
            max-width: 80%;
        }
        
        /* Data result styling - Improved from the red highlight */
        .data-result {
            background-color: #F1F8FE;
            border-left: 4px solid #3DCD58;
            padding: 12px 15px;
            margin: 10px 0;
            border-radius: 4px;
            font-family: 'Roboto Mono', monospace;
            font-size: 14px;
            overflow-x: auto;
            color: #2C2E35;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        
        /* Table styling for results */
        .result-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 15px;
        }
        
        .result-table th {
            background-color: #E5F5E8;
            color: #009530;
            font-weight: 600;
            text-align: left;
            padding: 10px;
            border-bottom: 2px solid #3DCD58;
        }
        
        .result-table td {
            padding: 10px;
            border-bottom: 1px solid #E0E3E7;
        }
        
        .result-table tr:nth-child(even) {
            background-color: #F9FAFB;
        }
        
        .result-table tr:hover {
            background-color: #F1F8E9;
        }
        
        /* Input field */
        .stTextInput input {
            border-radius: 20px;
            border: 1px solid #E0E3E7;
            padding: 10px 15px;
        }
        
        /* Timestamp style */
        .timestamp {
            font-size: 0.8em;
            color: #90949c;
            margin-top: 2px;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            margin-top: 30px;
            font-size: 0.8em;
            color: #90949c;
        }
        
        /* Custom sidebar styling */
        .css-1l269bu {
            background-color: #2C2E35;
        }
        .css-1l269bu a {
            color: white;
        }
        
        /* Logo container */
        .logo-container {
            text-align: center;
            padding: 20px 0;
        }
        
        /* Header styling */
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #E0E3E7;
            margin-bottom: 20px;
        }
        
    </style>
    """, unsafe_allow_html=True)

# Function to add background image
def add_bg_from_base64(base64_string):
    encoded_string = base64_string
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            background-attachment: fixed;
            background-opacity: 0.1;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Schneider Electric logo as base64 (faded)
# This is a placeholder, you'll need to replace with the actual logo encoded in base64
def get_base64_logo():
    # This is a placeholder for the Schneider Electric logo
    # Replace this with the actual base64 encoded logo
    return "iVBORw0KGgoAAAANSUhEUgAAASwAAAEsCAYAAAB5fY51AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAFNSURBVHgB7dRBDQAhEAAwpYCF/TfBwkeQkE2YU7B5M7Nzjgh4zNYFQIWwgAwLyLCADAvIsIAMC8iwgAwLyLCADAvIsIAMC8iwgAwLyLCADAvIsIAMC8iwgAwLyLCADAvIsIAMC8iwgAwLyLCADAvIsIAMC8iwgAwLyLCADAvIsIAMC8iwgAwLyLCADAvIsIAMC8iwgAwLyLCADAvIsIAMC8iwgAwLyLCADAvIsIAMC8iwgAwLyLCADAvIsIAMC8iwgAwLyLCADAvIsIAMC8iwgAwLyLCADAvIsIAMC8iwgAwLyLCADAvIsIAMC8iwgAwLyLCADAvIsIAMC8iwgAwLyLCADAvIsIAMC8iwgAwLyLCADAvIsIAMC8iwgAwLyLCADAvIsIAMC8iwgAwLyLCADAvIsIAMC8iwgAwLyLCADAvIsIAMC8iwgAwLyLCAvr9uA4anF1D/AAAAAElFTkSuQmCC"

# Function to format Salesforce data results in a cleaner way
def format_salesforce_results(data_text):
    # Check if this looks like our "function_results" data
    if "<function_results>" in data_text:
        try:
            # Extract relevant information
            accounts = []
            # Process each line with function_results
            for line in data_text.split('\n'):
                if '"AnnualRevenue"' in line and '"Name"' in line:
                    # Extract revenue and name using basic parsing
                    parts = line.split('"Name":')
                    if len(parts) > 1:
                        name_part = parts[1].split('"')[1]
                        revenue_part = parts[0].split('"AnnualRevenue":')[1].split(',')[0].strip()
                        accounts.append({"name": name_part, "revenue": revenue_part})
            
            # Build an HTML table for better display
            if accounts:
                html = '<div class="data-result">'
                html += '<table class="result-table">'
                html += '<tr><th>Company</th><th>Annual Revenue</th></tr>'
                
                for account in accounts:
                    revenue_formatted = account["revenue"]
                    if revenue_formatted.replace(".", "").replace("E", "").replace("+", "").isdigit():
                        # Format scientific notation to a readable number
                        try:
                            value = float(revenue_formatted)
                            revenue_formatted = f"${value:,.2f}"
                        except:
                            pass
                    
                    html += f'<tr><td>{account["name"]}</td><td>{revenue_formatted}</td></tr>'
                
                html += '</table></div>'
                return html
        except:
            # If parsing fails, return a cleaner version of the original
            cleaned = data_text.replace("<function_results>", "").replace("</function_results>", "")
            return f'<div class="data-result"><pre>{cleaned}</pre></div>'
    
    # For numeric data results that look like accounts with revenue
    if all(x in data_text for x in ["Annual Revenue", "$"]):
        return f'<div class="data-result"><pre>{data_text}</pre></div>'
        
    # Return original if no special formatting is needed
    return data_text

# Initialize or load session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'is_first_message' not in st.session_state:
    st.session_state.is_first_message = True

# API configuration
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/salesforce_agent_driver_VG_api"
API_HEADERS = {
    "Authorization": "Bearer z7gxfLKED6GRxY4Fdwcd9gcoWgJd5Q4c",
    "Content-Type": "application/json"
}

# Function to call Salesforce agent API
def query_salesforce_agent(user_message):
    payload = [{
        "session_id": st.session_state.session_id,
        "messages": [{"content": user_message, "sl_role": "USER"}]
    }]
    
    try:
        response = requests.post(API_URL, headers=API_HEADERS, json=payload)
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        return result.get("response", "Sorry, I couldn't process your request.")
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return "I'm having trouble connecting to the Salesforce data service. Please try again later."
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return "An unexpected error occurred. Please try again."

# Apply styling
local_css()

# Add background with faded logo
add_bg_from_base64(get_base64_logo())

# App layout
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    # Header
    st.markdown('<div class="header">', unsafe_allow_html=True)
    st.title("⚡ Schneider Electric Salesforce Assistant")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Introduction
    if st.session_state.is_first_message:
        st.markdown("""
        <div class="bot-message">
            <b>Welcome to the Schneider Electric Salesforce Assistant!</b><br>
            I can help you query Salesforce data using natural language. Try asking me something like:
            <ul>
                <li>Show me recent leads</li>
                <li>Find contacts from Zenith Industrial Partners</li>
                <li>Get open opportunities worth more than $50,000</li>
            </ul>
            How can I assist you today?
            <div class="timestamp">Today, {}</div>
        </div>
        """.format(datetime.now().strftime("%I:%M %p")), unsafe_allow_html=True)
    
    # Chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                {message["content"]}
                <div class="timestamp">{message["timestamp"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Process bot messages to improve formatting of data results
            content = format_salesforce_results(message["content"])
            st.markdown(f"""
            <div class="bot-message">
                {content}
                <div class="timestamp">{message["timestamp"]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input area
    with st.form(key="message_form", clear_on_submit=True):
        user_input = st.text_input("Type your question about Salesforce data...", 
                                  key="user_input", 
                                  placeholder="e.g., Show me the top 5 accounts by revenue")
        submit_button = st.form_submit_button("Send")
        
        if submit_button and user_input:
            # Add user message to chat
            timestamp = datetime.now().strftime("%I:%M %p")
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": timestamp
            })
            
            # Get response from API
            response = query_salesforce_agent(user_input)
            
            # Add assistant response to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": timestamp
            })
            
            st.session_state.is_first_message = False
            
            # Rerun to display the new messages
            st.rerun()
    
    # Footer
    st.markdown("""
    <div class="footer">
        © 2025 Schneider Electric. All rights reserved.<br>
        Powered by Schneider Electric AI Services.
    </div>
    """, unsafe_allow_html=True)

# Sidebar with additional information
with st.sidebar:
    st.image("https://www.se.com/ww/en/assets/564/media/60926/SE_logo_Life-Is-On_White_RGB.svg", width=200)
    st.markdown("<h3 style='color:white;'>Help & Information</h3>", unsafe_allow_html=True)
    
    with st.expander("📚 What can I ask?"):
        st.markdown("""
        You can ask natural language questions about your Salesforce data, such as:
        - Show me leads created this month
        - Find contacts at Microsoft
        - List opportunities closing this quarter
        - Get accounts in the healthcare industry
        """)
    
    with st.expander("🔍 Example queries"):
        st.markdown("""
        - Show me the top 5 accounts by revenue
        - Find leads with status 'Qualified'
        - List opportunities in the negotiation stage
        - Get contacts who haven't been contacted in 30 days
        """)
    
    with st.expander("❓ Need help?"):
        st.markdown("""
        If you're experiencing any issues with the assistant, please contact the IT Service Desk:
        - Email: support@schneider-electric.com
        - Phone: +1-800-555-1234
        """)
