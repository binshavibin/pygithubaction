import streamlit as st
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

st.title("SimpleChat")

# Initialize history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Helper to show aligned message bubbles
def message_bubble(role, text):
    if role == "assistant":
        left, right = st.columns([3, 1])
        with left:
            st.markdown(
                f'<div style="background:#e0e0e0; padding:10px; border-radius:10px; max-width:70%;">{text}</div>',
                unsafe_allow_html=True
            )
    else:
        left, right = st.columns([1, 3])
        with right:
            st.markdown(
                f'<div style="background:#0078d7; color:white; padding:10px; border-radius:10px; max-width:70%;">{text}</div>',
                unsafe_allow_html=True
            )

# Display chat history
for msg in st.session_state.messages:
    message_bubble(msg["role"], msg["content"])

# User input
if prompt := st.chat_input("Type your message..."):
    # Save and display user
    st.session_state.messages.append({"role": "user", "content": prompt})
    message_bubble("user", prompt)

    # Prepare Groq API call
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "llama-3.3-70b-versatile",  # choose a Groq model
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if m["role"] != "assistant"],
            {"role": "user", "content": prompt},
        ],
        "stream": False
    }

    # Send request to Groq chat completions API
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json=body,
        headers=headers,
    )

    assistant_reply = ""
    if response.status_code == 200:
        # Extract text from Groq response
        data = response.json()
        assistant_reply = data["choices"][0]["message"]["content"]
    else:
        assistant_reply = f"Error: {response.text}"

    # Display and save assistant reply
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    message_bubble("assistant", assistant_reply)