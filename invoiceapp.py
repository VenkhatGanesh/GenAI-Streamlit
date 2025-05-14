import streamlit as st
import requests
import json
import time
import base64
import os

# Set page configuration
st.set_page_config(
    page_title="Invoice Comparison Tool",
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
st.title("Invoice Comparison Tool")
st.markdown("""
This application allows you to upload multiple invoice PDF files and compare them using the processing API.
""")

# Create a file uploader widget that accepts PDF files
uploaded_files = st.file_uploader("Upload Invoice PDF files", type=['pdf'], accept_multiple_files=True)

# Initialize session state if it doesn't exist
if 'upload_history' not in st.session_state:
    st.session_state.upload_history = []

# Process the uploaded files
if uploaded_files and st.button("Compare Invoice"):
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
                st.success(f"Successfully processed {file_name}")
            else:
                # Add failed upload to history
                st.session_state.upload_history.append({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "filename": file_name,
                    "status": "Failed",
                    "response": f"Error {response.status_code}: {response.text}"
                })
                st.error(f"Failed to process {file_name}. Error: {response.status_code} - {response.text}")
        
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

# Display upload history
if st.session_state.upload_history:
    st.markdown("### Processing History")
    
    # Display each history item in a separate expander
    for idx, item in enumerate(reversed(st.session_state.upload_history)):
        with st.expander(f"{item['filename']} - {item['status']} ({item['timestamp']})"):
            st.write(f"**Timestamp:** {item['timestamp']}")
            st.write(f"**Filename:** {item['filename']}")
            st.write(f"**Status:** {item['status']}")
            st.write(f"**Response:** {item['response']}")
    
    # Add option to clear history
    if st.button("Clear Upload History"):
        st.session_state.upload_history = []
        # Use st.rerun() instead of experimental_rerun
        st.rerun()
