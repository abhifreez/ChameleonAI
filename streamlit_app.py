import streamlit as st
import os
from datetime import datetime
import json
import requests
import hmac
import base64
from datetime import timedelta
from mcp_utils import MCPClient
import asyncio
# from mcp_component import render_mcp_interface

# Set page config
st.set_page_config(
    page_title="ChameleonAI Chat",
    page_icon="🦎",
    layout="wide"
)

# Define credentials
credentials = {
    "admin": "admin123",
    "user1": "password123",
    "user2": "password456"
}

mcp_client = MCPClient()


def check_password():
    """Returns `True` if the user had a correct password."""
   

    # Check if the user is already authenticated
    if st.session_state.get('authenticated'):
        return True

    # Initialize session state
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0

    # Create login form
    with st.form("Credentials"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if username in credentials and credentials[username] == password:
                # Set authentication in session state
                st.session_state.authenticated = True
                st.session_state.username = username
                
                # Store authentication in query params
                st.query_params["authenticated"] = base64.b64encode(username.encode()).decode()
                st.rerun()  # Rerun to update the UI with new authentication state
            else:
                st.session_state.login_attempts += 1
                st.error("😕 Invalid username or password")
                return False
    
    # Check URL parameters for authentication
    if "authenticated" in st.query_params:
        try:
            username = base64.b64decode(st.query_params["authenticated"].encode()).decode()
            if username in credentials:
                st.session_state.authenticated = True
                st.session_state.username = username
                return True
        except:
            pass
    
    return False

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Check URL parameters for authentication on page load
if not st.session_state.get('authenticated') and "authenticated" in st.query_params:
    try:
        username = base64.b64decode(st.query_params["authenticated"].encode()).decode()
        if username in credentials:
            st.session_state.authenticated = True
            st.session_state.username = username
    except:
        pass

# Initialize session state for chat history and lecture inputs
if "messages" not in st.session_state:
    st.session_state.messages = []
if "lecture_title" not in st.session_state:
    st.session_state.lecture_title = ""
if "topics" not in st.session_state:
    st.session_state.topics = []

# Custom CSS for better chat appearance
st.markdown("""
<style>
.stChatMessage {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    background-color: #1E1E1E;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    border: 1px solid #333333;
    color: #FFFFFF;
}
.stChatMessage:hover {
    background-color: #2D2D2D;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}
.stMarkdown {
    color: #FFFFFF;
}
.stMarkdown p {
    margin-bottom: 0.5rem;
    color: #FFFFFF;
}
.file-box {
    background-color: #2D2D2D;
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #404040;
    margin: 0.5rem 0;
    color: #FFFFFF;
}
.file-box:hover {
    background-color: #383838;
}
/* Chat interface styling */
.main-content {
    display: flex;
    flex-direction: column;
    height: 100vh;
    padding: 1rem;
    background-color: #121212;
}
.chat-messages {
    flex-grow: 1;
    overflow-y: auto;
    margin-bottom: 1rem;
    padding: 1rem;
    background-color: #121212;
}
.chat-input {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 1rem;
    background-color: #1E1E1E;
    border-top: 1px solid #333333;
}
/* About section styling */
.sidebar .stMarkdown {
    color: #FFFFFF;
    background-color: rgba(255, 255, 255, 0.1);
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
.sidebar .stMarkdown h3 {
    color: #FFFFFF;
    margin-bottom: 1rem;
}
/* Override Streamlit's default white background */
.stApp {
    background-color: #121212;
}
/* Style headings in chat */
.stChatMessage h3 {
    color: #FFFFFF;
    margin-bottom: 1rem;
}
/* Header menu button styling */
button[data-testid="baseButton-header"] {
    margin-right: 40px;
}
/* Logout button styling */
.logout-button {
    position: fixed !important;
    right: 60px;
    top: 0;
    height: 48px;
    padding: 0 8px;
    z-index: 1000000;
    background-color: transparent !important;
    border: none !important;
    color: rgb(250, 250, 250) !important;
}
.logout-button:hover {
    color: rgb(255, 255, 255) !important;
    background-color: rgba(255, 255, 255, 0.1) !important;
}
</style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = "http://127.0.0.1:5000"  # Update this with your actual API URL
API_KEY = "9f8d1a2e-4c3b-4657-b29d-7e67c2a8f3d1"

def generate_content(messages, model_name="deepseek"):
    """Send request to the content generation service"""
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Check if this is a hardware-related query based on content_type
    # Check if this is a hardware-related query based on content_type
    content_type = st.session_state.get("content_type", "general")
    if "Hardware Generator" in content_type:
        try:
            response = requests.post(f"{API_URL}/hardware-generator", headers=headers, json={
                "user_prompt": messages
            })
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            return f"Error generating hardware content: {str(e)}"
    
    # For general queries
    elif "General Content" in content_type:
        try:
            response = requests.post(f"{API_URL}/general-chat", headers=headers, json={
                "user_prompt": messages
            })
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            return f"Error generating response: {str(e)}"

   

def generate_lecture_content(lecture_title, topics):
    """Generate lecture content using the lecture generation endpoint"""
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "lecture_title": lecture_title,
        "topics": topics
    }
    
    try:
        response = requests.post(f"{API_URL}/generate-lecture", headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"status": "error", "message": f"Error generating lecture content: {str(e)}"}

def format_response(response):
    """Format the response for display in Streamlit"""
    if isinstance(response, str):
        return response
        
    if isinstance(response, dict):
        if response.get("status") == "error":
            return f"❌ Error: {response.get('message', 'Unknown error occurred')}"
            
        if response.get("status") == "success":
            output = []
            
            # Display file paths with download buttons
            files_to_display = [
                ("📝 Lecture Details", response.get("lecture_details_file")),
                ("📚 Notes", response.get("notes_file"))
            ]
            
            for label, file_info in files_to_display:
                if file_info:
                    output.append(f"### {label}")
                    output.append(f'<div class="file-box">')
                    output.append(f'<p>File: {file_info["filename"]}</p>')
                    output.append(f'<a href="{API_URL}{file_info["download_url"]}" target="_blank" download>')
                    output.append(f'<button style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px;">Download File</button>')
                    output.append('</a>')
                    output.append('</div>')
            
            return "\n".join(output)
            
    return "Unexpected response format"

# Main application logic
if check_password():
    # Add logout button to header using container
    header_container = st.container()
    with header_container:
        st.markdown(
            """
            <style>
            [data-testid="stHeader"] {
                position: relative;
            }
            div[data-testid="stToolbar"] {
                position: relative;
                z-index: 999999;
            }
            .logout-btn-container {
                position: fixed;
                right: 60px;
                top: 0;
                height: 48px;
                z-index: 999999;
                background-color: transparent;
            }
            .logout-btn-container button {
                background-color: transparent;
                border: none;
                color: rgb(250, 250, 250);
                cursor: pointer;
                height: 48px;
                padding: 0 8px;
            }
            .logout-btn-container button:hover {
                color: rgb(255, 255, 255);
                background-color: rgba(255, 255, 255, 0.1);
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # # Create a container for the logout button
        # st.markdown(
        #     """
        #     <div class="logout-btn-container">
        #         <button onclick="document.getElementById('logout-trigger').click()">
        #             Logout
        #         </button>
        #     </div>
        #     """,
        #     unsafe_allow_html=True
        # )
        
        # Hidden button that will be triggered by the custom button
        
    
    # Sidebar content
    with st.sidebar:
        st.title("🦎 Sunstone AI")
        st.markdown("---")
        st.markdown("""
        <h3 style="color: white;">About</h3>
        <p style="color: white;">This is a chat interface for the ChameleonAI content generation service.
        You can interact with the AI to generate various types of content.</p>
        """, unsafe_allow_html=True)
        
        # Content type selection
        content_type = st.selectbox(
            "Select Content Type",
            ["Lecture Content", "General Content", "MCP Interface", "Hardware Generator"]
        )
        st.session_state["content_type"] = content_type
        # Add lecture content input fields when Lecture Content is selected
        if content_type == "Lecture Content":
            st.markdown("### Lecture Details")
            temp_lecture_title = st.text_input("Lecture Title", placeholder="Enter the lecture title")
            
            # Topics input
            st.markdown("### Topics")
            num_topics = st.number_input("Number of Topics", min_value=1, max_value=10, value=3)
            temp_topics = []
            for i in range(num_topics):
                topic = st.text_input(f"Topic {i+1}", key=f"topic_{i}")
                if topic:
                    temp_topics.append(topic)
            
            # Add Apply button for lecture inputs
            if st.button("Apply Lecture Settings"):
                if not temp_lecture_title or not temp_topics:
                    st.error("Please provide both lecture title and at least one topic.")
                else:
                    st.session_state.lecture_title = temp_lecture_title
                    st.session_state.topics = temp_topics
                    
                    # Generate lecture content immediately
                    with st.spinner("Generating lecture content..."):
                        response = generate_lecture_content(temp_lecture_title, temp_topics)
                        formatted_response = format_response(response)
                        
                        # Add the interaction to chat history
                        settings_msg = f"Applied lecture settings:\nTitle: {temp_lecture_title}\nTopics: {', '.join(temp_topics)}"
                        st.session_state.messages.append({"role": "user", "content": settings_msg})
                        st.session_state.messages.append({"role": "assistant", "content": formatted_response})
                        
                        st.success("Lecture settings applied and content generated!")
                        st.rerun()  # Refresh to show the new messages
        
        if st.button("Logout", key="logout-trigger", type="secondary"):
            st.session_state.authenticated = False
            st.session_state.username = None
            if "authenticated" in st.query_params:
                del st.query_params["authenticated"]
            st.rerun()

    # In your main content area, add this condition
    if content_type == "MCP Interface":
        #render_mcp_interface()
        asyncio.run(mcp_client.connect_to_server(server_script_path="mcp_server/server.py"))
        print("MCP Interface")
       
    else:
        # Main chat interface
        prompt = st.chat_input("What would you like to generate?")
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"<h3>Welcome {st.session_state.username}!</h3>", unsafe_allow_html=True)
        with col2:
            click = st.button("🗑️ Clear Chat", help="Remove all chat messages")
        if click:
            st.session_state.messages = []
            st.rerun()
      
            
        
        # Create main content container
        main_content = st.container()
        with main_content:
            # Messages container
            messages_container = st.container()
            with messages_container:
                # Display chat messages
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"], unsafe_allow_html=True)
                

         
            
            # Chat input container (always at the bottom)
            input_container = st.container()
            with input_container:
                # Only show chat input for General Content
                if content_type != "Content Generator":
                    if prompt :
                        # Add user message to chat history
                        st.session_state.messages.append({"role": "user", "content": prompt})
                        
                        # Display user message
                        with st.chat_message("user"):
                            st.markdown(prompt)
                        
                        # Display assistant message
                        with st.chat_message("assistant"):
                            with st.spinner("Generating response..."):
                                response = generate_content(st.session_state.messages)
                                formatted_response = format_response(response)
                                st.markdown(formatted_response, unsafe_allow_html=True)
                                st.session_state.messages.append({"role": "assistant", "content": formatted_response})

        # Add a download button for chat history
        if st.session_state.messages:
            chat_history = json.dumps(st.session_state.messages, indent=2)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chat_history_{timestamp}.json"
            
            # st.download_button(
            #     label="Download Chat History",
            #     data=chat_history,
            #     file_name=filename,
            #     mime="application/json"
            # ) 