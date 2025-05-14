import streamlit as st
import requests
import json
import time
import base64
import os

# Set page configuration
st.set_page_config(
    page_title="Invoice Upload Tool",
    page_icon="📝",
    layout="centered"
)

# Define API details
API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/post-file-tool_API"
API_TOKEN = "SWXx74parYQZkO4L8rW6eiMkpzGOCUAj"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}

# App title and description
st.title("Invoice Upload Tool")
st.markdown("""
This application allows you to upload multiple invoice PDF files and submit them to the processing API.
""")

# Create a file uploader widget that accepts PDF files
uploaded_files = st.file_uploader("Upload Invoice PDF files", type=['pdf'], accept_multiple_files=True)

# Initialize session state if it doesn't exist
if 'upload_history' not in st.session_state:
    st.session_state.upload_history = []

# Process the uploaded files
if uploaded_files and st.button("Submit Invoices"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, uploaded_file in enumerate(uploaded_files):
        # Display processing status
        file_name = uploaded_file.name
        status_text.text(f"Processing {file_name}... ({i+1}/{len(uploaded_files)})")
        
        try:
            # Read the file content
            file_content = uploaded_file.read()
            
            # Send the file to the API
            response = requests.post(
                url=f"{API_URL}?filename={file_name}",
                headers=HEADERS,
                data=file_content,
                timeout=30
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                response_data = response.json()
                # Add to upload history with timestamp
                st.session_state.upload_history.append({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "filename": file_name,
                    "status": "Success",
                    "response": response_data
                })
                st.success(f"Successfully uploaded {file_name}")
            else:
                # Add failed upload to history
                st.session_state.upload_history.append({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "filename": file_name,
                    "status": "Failed",
                    "response": f"Error {response.status_code}: {response.text}"
                })
                st.error(f"Failed to upload {file_name}. Error: {response.status_code} - {response.text}")
        
        except Exception as e:
            # Add error to history
            st.session_state.upload_history.append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "filename": file_name,
                "status": "Error",
                "response": str(e)
            })
            st.error(f"Error processing {file_name}: {str(e)}")
        
        # Update progress bar
        progress_bar.progress((i + 1) / len(uploaded_files))
    
    status_text.text("Processing complete!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()

# Display chat interface
st.markdown("### Chat Support")
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
prompt = st.chat_input("Ask a question about invoice uploads...")
if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Prepare assistant response
    assistant_response = ""
    
    # Simple response logic based on keywords
    prompt_lower = prompt.lower()
    if "how" in prompt_lower and "upload" in prompt_lower:
        assistant_response = "To upload invoices, click the 'Browse files' button above, select one or more PDF files, then click 'Submit Invoices'."
    elif "format" in prompt_lower or "file type" in prompt_lower:
        assistant_response = "This tool accepts invoice files in PDF format only."
    elif "history" in prompt_lower or "previous" in prompt_lower:
        assistant_response = "You can view your upload history in the table below the chat interface."
    elif "error" in prompt_lower or "fail" in prompt_lower:
        assistant_response = "If you're experiencing errors, please ensure your files are valid PDFs and try again. If problems persist, check your network connection."
    elif "api" in prompt_lower or "endpoint" in prompt_lower:
        assistant_response = "The system is using a secure API endpoint to process your invoice files. Your data is being transmitted securely."
    else:
        assistant_response = "I'm your invoice upload assistant. I can help you upload PDF invoices to our processing system. Feel free to ask if you have any questions!"
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    
    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(assistant_response)

# Display upload history
if st.session_state.upload_history:
    st.markdown("### Upload History")
    
    # Create a dataframe-like display of upload history
    st.markdown("| Timestamp | Filename | Status | Response |")
    st.markdown("|-----------|----------|--------|----------|")
    
    # Display most recent uploads first
    for item in reversed(st.session_state.upload_history):
        # Truncate response for display if it's too long
        response_display = str(item["response"])
        if len(response_display) > 50:
            response_display = response_display[:47] + "..."
        
        st.markdown(f"| {item['timestamp']} | {item['filename']} | {item['status']} | {response_display} |")
    
    # Add option to clear history
    if st.button("Clear Upload History"):
        st.session_state.upload_history = []
        st.experimental_rerun()