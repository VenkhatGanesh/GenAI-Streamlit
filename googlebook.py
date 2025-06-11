import streamlit as st
import requests
import json
import uuid
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="📚 Book Discovery Chatbot",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for multi-color background and styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, 
            #667eea 0%, 
            #764ba2 25%, 
            #f093fb 50%, 
            #f5576c 75%, 
            #4facfe 100%);
        background-size: 400% 400%;
        animation: gradientShift 10s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .chat-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .user-message {
        background: rgba(100, 149, 237, 0.3);
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 4px solid #6495ED;
    }
    
    .assistant-message {
        background: rgba(144, 238, 144, 0.3);
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 4px solid #90EE90;
    }
    
    .book-card {
        background: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    .title-text {
        color: white;
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
    }
    
    .subtitle-text {
        color: white;
        text-align: center;
        font-size: 1.5rem;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/GoogleBooks_agent_driver_api"
HEADERS = {
    "Authorization": "Bearer OuOBD5JnFNduAJeBV7F2GQgdfQKbBJcM",
    "Content-Type": "application/json"
}

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'show_api_test' not in st.session_state:
    st.session_state.show_api_test = False
if 'api_test_result' not in st.session_state:
    st.session_state.api_test_result = None
if 'is_searching' not in st.session_state:
    st.session_state.is_searching = False

def call_books_api(user_message):
    """Call the Google Books API through the provided endpoint"""
    payload = [{
        "session_id": st.session_state.session_id,
        "messages": st.session_state.messages + [
            {"content": user_message, "sl_role": "USER"}
        ]
    }]
    
    try:
        # Try with a longer timeout and more detailed error handling
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Connection timeout - The API is taking too long to respond. Please try again in a moment."}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection failed - Unable to reach the API endpoint. Please check your internet connection."}
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"API Error: {str(e)}"}

def display_message(message, is_user=True):
    """Display a chat message with appropriate styling"""
    if is_user:
        st.markdown(f"""
        <div class="user-message">
            <strong>🧑‍💻 You:</strong><br>
            {message}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="assistant-message">
            <strong>🤖 Book Assistant:</strong><br>
            {message}
        </div>
        """, unsafe_allow_html=True)

def main():
    # Title and header
    st.markdown('<h1 class="title-text">📚 Book Discovery Chatbot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Discover amazing books through conversation!</p>', unsafe_allow_html=True)
    
    # Sidebar with information
    with st.sidebar:
        # Top buttons in two columns
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 New Chat", key="new_conv", disabled=st.session_state.is_searching):
                st.session_state.messages = []
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.show_api_test = False  # Reset API test state
                st.session_state.is_searching = False  # Reset searching state
                st.rerun()
        
        with col2:
            if st.button("🔍 Test API", key="test_api", disabled=st.session_state.is_searching):
                st.session_state.show_api_test = True
                st.rerun()
        
        st.markdown("---")
        st.markdown(f"**Session:** `{st.session_state.session_id[:8]}...`")
        st.markdown("---")
        
        # Collapsible About section
        with st.expander("📖 About This Chatbot", expanded=False):
            st.markdown("""
            This intelligent chatbot helps you discover books using natural conversation. 
            You can ask about:
            
            - 📚 Books by specific authors
            - 🌸 Books on particular topics  
            - 📖 Book recommendations
            - 📋 Detailed book information
            - ⭐ Reviews and ratings
            """)
        
        # Collapsible Examples section
        with st.expander("💡 Example Queries", expanded=False):
            st.markdown("""
            Try asking:
            
            - "Can you share details of books about flowers by Keyes?"
            - "Find me science fiction novels"
            - "What are the best cooking books?"
            - "Show me books by Stephen King"
            """)

    # API Test Modal
    if st.session_state.show_api_test:
        @st.dialog("🔍 API Connection Test", width="large")
        def test_api_modal():
            # Prevent modal from closing by clicking outside during test
            if 'api_test_started' not in st.session_state:
                st.session_state.api_test_started = False
            if 'api_test_completed' not in st.session_state:
                st.session_state.api_test_completed = False
            
            st.write("Testing connection to Google Books API...")
            
            # Start the test automatically when modal opens
            if not st.session_state.api_test_started:
                st.session_state.api_test_started = True
                with st.spinner("Connecting..."):
                    test_response = call_books_api("test connection")
                    st.session_state.api_test_result = test_response
                    st.session_state.api_test_completed = True
                st.rerun()
            
            # Show results if test is completed
            if st.session_state.api_test_completed:
                test_response = st.session_state.api_test_result
                
                if "error" in test_response:
                    st.error("❌ **Connection Failed**")
                    st.code(test_response['error'], language="text")
                    st.write("**Possible solutions:**")
                    st.write("• Check your internet connection")
                    st.write("• Try again in a few moments")
                    st.write("• Verify API endpoint accessibility")
                else:
                    st.success("✅ **API Connection Successful!**")
                    st.write("The Google Books API is responding correctly.")
                    st.json({"status": "connected", "session_id": st.session_state.session_id[:8]})
                
                # Only show close button after test is completed
                if st.button("Close", type="primary", use_container_width=True):
                    st.session_state.show_api_test = False
                    st.session_state.api_test_started = False
                    st.session_state.api_test_completed = False
                    st.session_state.api_test_result = None
                    st.rerun()
            else:
                # Show connecting status
                st.info("🔄 Connecting to API... Please wait.")
        
        test_api_modal()

    # Main chat interface
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat history
        if st.session_state.messages:
            st.markdown("### 💬 Conversation History")
            for message in st.session_state.messages:
                if message['sl_role'] == 'USER':
                    display_message(message['content'], is_user=True)
                else:
                    display_message(message['content'], is_user=False)
        else:
            st.markdown("""
            <div class="book-card">
                <h3>👋 Welcome to your Book Discovery Assistant!</h3>
                <p>I'm here to help you find amazing books. Just ask me about any book, author, or topic you're interested in!</p>
                <p><strong>Try asking:</strong> "Can you recommend some mystery novels?" or "Tell me about books by Agatha Christie"</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Chat input
    with st.container():
        st.markdown("### 💭 Ask me about books...")
        
        # Create columns for input and button
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "Your message:",
                placeholder="e.g., Can you tell me about books on artificial intelligence?",
                key="user_input"
            )
        
        with col2:
            send_button = st.button("📤 Send", type="primary", disabled=st.session_state.is_searching)

    # Handle user input
    if send_button and user_input and not st.session_state.is_searching:
        # IMPORTANT FIX: Reset the API test modal state when sending a message
        st.session_state.show_api_test = False
        st.session_state.is_searching = True  # Set searching state
        
        # Add user message to session state
        st.session_state.messages.append({
            "content": user_input,
            "sl_role": "USER"
        })
        
        # Show thinking message
        with st.spinner("🔍 Searching for books..."):
            # Call the API
            api_response = call_books_api(user_input)
            
            if "error" in api_response:
                assistant_response = f"""
                I apologize, but I encountered an issue while searching for books: 
                
                **{api_response['error']}**
                
                🔧 **Troubleshooting Tips:**
                - Check if your internet connection is stable
                - Try again in a few moments - the API might be temporarily busy
                - Verify that the API endpoint is accessible from your network
                
                In the meantime, I can suggest some general book recommendations based on your query about "{user_input}". Would you like me to provide some general suggestions?
                """
            else:
                assistant_response = api_response.get("response", "I found some information, but couldn't format it properly.")
            
            # Add assistant response to session state
            st.session_state.messages.append({
                "content": assistant_response,
                "sl_role": "ASSISTANT"
            })
        
        # Reset searching state
        st.session_state.is_searching = False
        
        # Rerun to update the display
        st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: white; font-size: 0.9rem;">
        <p>📚 Powered by Google Books API | Built with Streamlit</p>
        <p>Happy Reading! 🌟</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
