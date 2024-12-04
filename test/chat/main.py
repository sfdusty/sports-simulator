import streamlit as st
import openai
import os
import json
from datetime import datetime
from streamlit_chat import message  # Ensure this is installed: pip install streamlit-chat

# -----------------------------
# Function Definitions
# -----------------------------

def load_api_key(config_path="chat/config/config.json"):
    """
    Retrieves the OpenAI API key from the config.json file.
    """
    if not os.path.exists(config_path):
        st.error(f"Config file not found at {config_path}. Please ensure the file exists.")
        st.stop()
    
    with open(config_path, "r") as f:
        try:
            config = json.load(f)
            api_key = config.get("OPENAI_API_KEY")
            if not api_key:
                st.error("OPENAI_API_KEY not found in config.json.")
                st.stop()
            return api_key
        except json.JSONDecodeError:
            st.error("Invalid JSON format in config.json.")
            st.stop()

def load_conversations():
    """
    Loads conversation histories from a JSON file into session state.
    """
    if "conversations" not in st.session_state:
        conversations_file = "conversations.json"
        if os.path.exists(conversations_file):
            with open(conversations_file, "r") as f:
                try:
                    st.session_state.conversations = json.load(f)
                except json.JSONDecodeError:
                    st.error("Invalid JSON format in conversations.json.")
                    st.session_state.conversations = {}
        else:
            st.session_state.conversations = {}
    return st.session_state.conversations

def save_conversations():
    """
    Saves conversation histories from session state to a JSON file.
    """
    with open("conversations.json", "w") as f:
        json.dump(st.session_state.conversations, f, indent=4)

def initialize_conversation():
    """
    Initializes a new conversation if none exists in session state.
    """
    if "current_conversation" not in st.session_state:
        st.session_state.current_conversation = {
            "title": f"Conversation {len(st.session_state.conversations) + 1}",
            "messages": []
        }

def switch_conversation(conversation_key):
    """
    Switches to a selected conversation based on its key.
    """
    st.session_state.current_conversation = st.session_state.conversations[conversation_key]

def display_conversation():
    """
    Displays the conversation history in the main chat area using streamlit-chat.
    """
    for msg in st.session_state.current_conversation["messages"]:
        if msg["role"] == "user":
            message(msg["content"], is_user=True, key=msg["timestamp"])
        elif msg["role"] == "assistant":
            message(msg["content"], is_user=False, key=msg["timestamp"])

def scroll_to_bottom():
    """
    Injects JavaScript to scroll the chat container to the bottom.
    """
    scroll_script = """
    <script>
    const chatContainer = document.querySelector('.css-1v3fvcr.e1tzin5v3'); // Adjust the selector if necessary
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    </script>
    """
    st.markdown(scroll_script, unsafe_allow_html=True)

# -----------------------------
# Initialization
# -----------------------------

# Set page configuration
st.set_page_config(page_title="OpenAI Chatbot", layout="wide")

# Load API key
openai.api_key = load_api_key()

# Load conversations
conversations = load_conversations()

# Initialize current conversation
initialize_conversation()

# -----------------------------
# Sidebar Configuration
# -----------------------------

st.sidebar.title("Chatbot Settings")

# Model Selection
model_options = ["gpt-4", "gpt-3.5-turbo"]
selected_model = st.sidebar.selectbox("Select Model", options=model_options, index=0)

# Token Limit Slider
max_tokens = st.sidebar.slider(
    "Max Tokens",
    min_value=50,
    max_value=2048,
    value=150,
    step=50,
    help="Maximum number of tokens in the response."
)

# Temperature Slider
temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.1,
    help="Controls the randomness of the model's output. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic."
)

st.sidebar.markdown("---")

st.sidebar.title("Conversation History")

# List existing conversations
if st.session_state.conversations:
    selected_conv = st.sidebar.selectbox(
        "Select a Conversation",
        options=list(st.session_state.conversations.keys()),
        format_func=lambda x: st.session_state.conversations[x]["title"]
    )
    load_button = st.sidebar.button("Load Conversation")
    delete_button = st.sidebar.button("Delete Conversation")

    if load_button:
        switch_conversation(selected_conv)
    if delete_button:
        del st.session_state.conversations[selected_conv]
        save_conversations()
        st.sidebar.success(f"Deleted conversation: {selected_conv}")
        # Initialize a new conversation after deletion
        new_conv_title = f"Conversation {len(st.session_state.conversations) + 1}"
        st.session_state.current_conversation = {
            "title": new_conv_title,
            "messages": []
        }
else:
    st.sidebar.info("No conversations yet.")

# Option to start a new conversation
if st.sidebar.button("Start New Conversation"):
    new_conv_title = f"Conversation {len(st.session_state.conversations) + 1}"
    st.session_state.current_conversation = {
        "title": new_conv_title,
        "messages": []
    }

# Option to rename the current conversation
if st.session_state.current_conversation["messages"]:
    if st.sidebar.button("Rename Conversation"):
        new_title = st.sidebar.text_input("Enter a new name for this conversation:", key="rename_conv")
        if new_title:
            old_title = st.session_state.current_conversation["title"]
            st.session_state.current_conversation["title"] = new_title
            st.session_state.conversations[new_title] = st.session_state.current_conversation
            del st.session_state.conversations[old_title]
            save_conversations()
            st.sidebar.success(f"Conversation renamed to: {new_title}")

# -----------------------------
# Main Interface Configuration
# -----------------------------

# Header
st.header(st.session_state.current_conversation["title"])

# Chat container using streamlit-chat
chat_placeholder = st.empty()

with chat_placeholder.container():
    display_conversation()

# Input form fixed at the bottom
st.markdown("""---""")
with st.form(key='user_input_form', clear_on_submit=True):
    user_input = st.text_input("You:", placeholder="Type your message here...")
    submit_button = st.form_submit_button(label='Send')

# Handle form submission
if submit_button and user_input:
    # Append user message to current conversation
    user_message = {
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().isoformat()
    }
    st.session_state.current_conversation["messages"].append(user_message)
    
    # Display user message
    with chat_placeholder.container():
        display_conversation()
    
    # Generate assistant response
    try:
        with st.spinner('Chatbot is typing...'):
            response = openai.ChatCompletion.create(
                model=selected_model,  # Use selected model
                messages=st.session_state.current_conversation["messages"],
                max_tokens=max_tokens,  # Use selected max_tokens
                temperature=temperature,  # Use selected temperature
            )
        assistant_reply = response.choices[0].message['content'].strip()
        assistant_message = {
            "role": "assistant",
            "content": assistant_reply,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.current_conversation["messages"].append(assistant_message)
        
        # Display assistant message
        with chat_placeholder.container():
            display_conversation()
    except openai.error.OpenAIError as e:
        st.error(f"An error occurred: {e}")

    # Save conversations
    conversations_key = st.session_state.current_conversation["title"]
    st.session_state.conversations[conversations_key] = st.session_state.current_conversation
    save_conversations()

    # Scroll to bottom (handled automatically by streamlit-chat)

