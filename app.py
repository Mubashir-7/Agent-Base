import streamlit as st
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
import uuid

# Custom CSS for professional styling
st.markdown("""
<style>
    .stApp {
        background-color: #f5f7fa;
        font-family: 'Arial', sans-serif;
    }
    .title {
        color: #1a73e8;
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .subtitle {
        color: #4a5568;
        text-align: center;
        font-size: 1.2em;
        margin-bottom: 1.5em;
    }
    .chat-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        max-height: 400px;
        overflow-y: auto;
        margin-bottom: 20px;
    }
    .chat-message {
        padding: 10px;
        margin: 5px 0;
        border-radius: 8px;
        font-size: 1em;
    }
    .user-message {
        background-color: #e6f3ff;
        color: #1a73e8;
        margin-left: 20%;
        margin-right: 5%;
    }
    .ai-message {
        background-color: #f1f1f1;
        color: #333;
        margin-right: 20%;
        margin-left: 5%;
    }
    .input-container {
        display: flex;
        gap: 10px;
        align-items: center;
    }
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #d1d5db;
        padding: 10px;
        font-size: 1em;
    }
    .stButton > button {
        background-color: #1a73e8;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 1em;
        border: none;
    }
    .stButton > button:hover {
        background-color: #1557b0;
    }
    .clear-button > button {
        background-color: #e53e3e;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 1em;
        border: none;
    }
    .clear-button > button:hover {
        background-color: #c53030;
    }
</style>
""", unsafe_allow_html=True)

# Load AI Model
llm = OllamaLLM(model="mistral")  # Change to "llama3" or another Ollama model

# Initialize Memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ChatMessageHistory()

# Define AI Chat Prompt
prompt = PromptTemplate(
    input_variables=["chat_history", "question"],
    template="Previous conversation: {chat_history}\nUser: {question}\nAI:"
)

# Function to run AI chat with memory
def run_chain(question):
    chat_history_text = "\n".join([f"{msg.type.capitalize()}: {msg.content}" for msg in st.session_state.chat_history.messages])
    response = llm.invoke(prompt.format(chat_history=chat_history_text, question=question))
    st.session_state.chat_history.add_user_message(question)
    st.session_state.chat_history.add_ai_message(response)
    return response

# Function to clear chat history
def clear_chat():
    st.session_state.chat_history = ChatMessageHistory()

# Streamlit UI
st.markdown('<div class="title">🤖 AI Chatbot with Memory</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask anything and enjoy a seamless conversation!</div>', unsafe_allow_html=True)

# Chat history display
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.chat_history.messages:
    if msg.type == "user":
        st.markdown(f'<div class="chat-message user-message"><b>You:</b> {msg.content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message ai-message"><b>AI:</b> {msg.content}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Input section
st.markdown('<div class="input-container">', unsafe_allow_html=True)
user_input = st.text_input("Your Question:", placeholder="Type your question here...", key="user_input")
submit_button = st.button("Send")
clear_button = st.button("Clear Chat", key="clear_button", help="Clear the chat history", type="secondary")

if submit_button and user_input:
    response = run_chain(user_input)
    st.experimental_rerun()  # Refresh to show new messages

if clear_button:
    clear_chat()
    st.experimental_rerun()

st.markdown('</div>', unsafe_allow_html=True)