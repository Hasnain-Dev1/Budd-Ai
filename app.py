import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load local .env file (if it exists)
load_dotenv()

# --- MeshAPI Configuration ---

MESH_API_KEY = st.secrets.get("MESH_API_KEY") or os.getenv("MESH_API_KEY")
MESH_BASE_URL = "https://api.meshapi.ai/v1" 
# Switched to gpt-4o-mini because MeshAPI is currently crashing on the Claude model
MODEL_NAME = "openai/gpt-4o-mini" 

# Safety check
if not MESH_API_KEY:
    st.error("🚨 API Key not found! Please create a `.env` file and add `MESH_API_KEY=your_key_here` inside it.")
    st.stop()

# Initialize the client
@st.cache_resource
def get_client():
    return OpenAI(
        api_key=MESH_API_KEY,
        base_url=MESH_BASE_URL
    )

client = get_client()

# --- Kid-Safe System Prompt ---
KID_SYSTEM_PROMPT = """
You are BuddyAI, a friendly, safe, and educational AI robot buddy for kids. 
Follow these rules strictly:
1. Use simple words that a 7-12 year old can understand.
2. Be enthusiastic, kind, and encouraging. Use emojis frequently! 🚀✨
3. NEVER use bad words, scary content, or mature themes.
4. If the kid asks something inappropriate, politely say "Let's talk about something else!" and suggest a fun topic like space, dinosaurs, or art.
5. Keep answers short (3-4 sentences max) and fun to read.
"""

# --- Initialize Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": KID_SYSTEM_PROMPT},
        {"role": "assistant", "content": "Hi there! I'm BuddyAI 🤖. What do you want to learn about today?"}
    ]

# --- UI Header ---
st.title("🤖 BuddyAI")
st.subheader("Your awesome learning buddy!")

# --- Quick Prompt Buttons ---
st.write("**✨ Try one of these!**")
col1, col2, col3 = st.columns(3)
if col1.button("🚀 Space Fact"):
    st.session_state.messages.append({"role": "user", "content": "Tell me a cool fact about space!"})
if col2.button("🦖 Dino Joke"):
    st.session_state.messages.append({"role": "user", "content": "Tell me a funny dinosaur joke."})
if col3.button("➗ Math Help"):
    st.session_state.messages.append({"role": "user", "content": "How do I multiply fractions?"})

# --- Display Chat History (Skip the system prompt) ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# --- Chat Input ---
if prompt := st.chat_input("Type your question here...", key="kid_chat_input"):
    # 1. Add user message to UI and history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 2. Call MeshAPI and get response
    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        thinking_placeholder.write("Thinking... 🧠")
        
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=st.session_state.messages,
                temperature=0.7 
            )
            
            bot_reply = response.choices[0].message.content
            thinking_placeholder.write(bot_reply)
            
            # Save to history
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            
        except Exception as e:
            error_msg = f"Oops! Something went wrong: {e}"
            if hasattr(e, 'response') and e.response is not None:
                error_details = e.response.text
                error_msg += f"\n\n**API Details:** {error_details}"
            thinking_placeholder.error(error_msg)