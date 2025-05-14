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
UPLOAD_API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/post-file-tool_API"
UPLOAD_API_TOKEN = "SWXx74parYQZkO4L8rW6eiMkpzGOCUAj"
UPLOAD_HEADERS = {
    "Authorization": f"Bearer {UPLOAD_API_TOKEN}"
}

COMPARE_API_URL = "https://emea.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/snapLogic4snapLogic/Training20250407/CompareInvoiceapi"
COMPARE_API_TOKEN = "nCMe9Ctzo0gkEvj2yoj6mbacRDe6b9dd"
COMPARE_HEADERS = {
    "Authorization": f"Bearer {COMPARE_API_TOKEN}"
}

# App title and description
st.title("Invoice Comparison Tool")
st.markdown("""
This application allows you to upload invoice PDF files and compare them using the processing API.
""")

# Create a file uploader widget that accepts PDF files
uploaded_files = st.file_uploader("Upload Invoice PDF files", type=['pdf'], accept_multiple_files=True)

# Initialize session state if it doesn't exist
if 'upload_history' not in st.session_state:
    st.session_state.upload_history = []

if 'files_uploaded' not in st.session_state:
    st.session_state.files_uploaded = False

if 'comparison_result' not in st.session_state:
    st.session_state.comparison_result = None

# Process the uploaded files - Upload button
if uploaded_files and st.button("Upload"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    upload_success = True
    
    for i, uploaded_file in enumerate(uploaded_files):
        # Display processing status
        file_name = uploaded_file.name
        status_text.text(f"Uploading {file_name}... ({i+1}/{len(uploaded_files)})")
        
        try:
            # Read the file content
            file_content = uploaded_file.read()
            
            # Send the file to the Upload API
            response = requests.post(
                url=f"{UPLOAD_API_URL}?filename={file_name}",
                headers=UPLOAD_HEADERS,
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
                    "status": "Uploaded",
                    "response": response_data
                })
                st.success(f"Successfully uploaded {file_name}")
            else:
                upload_success = False
                # Add failed upload to history
                st.session_state.upload_history.append({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "filename": file_name,
                    "status": "Failed",
                    "response": f"Error {response.status_code}: {response.text}"
                })
                st.error(f"Failed to upload {file_name}. Error: {response.status_code} - {response.text}")
        
        except Exception as e:
            upload_success = False
            # Add error to history
            st.session_state.upload_history.append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "filename": file_name,
                "status": "Error",
                "response": str(e)
            })
            st.error(f"Error uploading {file_name}: {str(e)}")
        
        # Update progress bar
        progress_bar.progress((i + 1) / len(uploaded_files))
    
    status_text.text("Upload complete!")
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()
    
    # Set files_uploaded to True if at least one file was uploaded successfully
    if upload_success:
        st.session_state.files_uploaded = True
        st.rerun()

# Compare button - only show if files have been uploaded
if st.session_state.files_uploaded:
    st.markdown("### Compare Uploaded Invoices")
    
    if st.button("Compare Invoice"):
        try:
            # Call the comparison API
            response = requests.post(
                url=COMPARE_API_URL,
                headers=COMPARE_HEADERS,
                json={},  # Empty JSON body as per your requirements
                timeout=30
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                comparison_data = response.json()
                st.session_state.comparison_result = comparison_data
                
                # Add to history
                st.session_state.upload_history.append({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "filename": "Comparison",
                    "status": "Success",
                    "response": comparison_data
                })
                
                st.success("Invoice comparison completed successfully!")
            else:
                st.error(f"Failed to compare invoices. Error: {response.status_code} - {response.text}")
                
                # Add to history
                st.session_state.upload_history.append({
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "filename": "Comparison",
                    "status": "Failed",
                    "response": f"Error {response.status_code}: {response.text}"
                })
        
        except Exception as e:
            st.error(f"Error comparing invoices: {str(e)}")
            
            # Add to history
            st.session_state.upload_history.append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "filename": "Comparison",
                "status": "Error",
                "response": str(e)
            })

# Display comparison results if available
if st.session_state.comparison_result:
    st.markdown("### Comparison Results")
    
    try:
        result = st.session_state.comparison_result
        
        # Display the formatted comparison result
        for item in result:
            if "content" in item:
                st.markdown("#### Analysis")
                st.markdown(item["content"])
            else:
                # If the structure is different, display as JSON
                st.json(item)
    except Exception as e:
        st.error(f"Error displaying comparison results: {str(e)}")

# Display processing history
if st.session_state.upload_history:
    st.markdown("### Processing History")
    
    # Display each history item in a separate expander
    for idx, item in enumerate(reversed(st.session_state.upload_history)):
        with st.expander(f"{item['filename']} - {item['status']} ({item['timestamp']})"):
            st.write(f"**Timestamp:** {item['timestamp']}")
            st.write(f"**Filename:** {item['filename']}")
            st.write(f"**Status:** {item['status']}")
            st.write(f"**Response:**")
            
            # Format the response based on its type
            if isinstance(item['response'], dict) or isinstance(item['response'], list):
                st.json(item['response'])
            else:
                st.write(item['response'])
    
    # Add option to clear history
    if st.button("Clear History"):
        st.session_state.upload_history = []
        st.session_state.files_uploaded = False
        st.session_state.comparison_result = None
        st.rerun()
