import streamlit as st
import pyttsx3
import speech_recognition as sr
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM


llm = OllamaLLM(model="mistral")  # change model if needed

prompt = PromptTemplate(
    input_variables=["chat_history", "question"],
    template="""
    You are a helpful AI voice assistant. Answer clearly and keep context.

    Chat history:
    {chat_history}

    Human: {question}
    AI:
    """
)


if "chat_history" not in st.session_state:
    st.session_state.chat_history = ChatMessageHistory()

if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": "user"/"ai", "content": text}


engine = pyttsx3.init()

def tts_speak(text: str):
    rate = st.session_state.get("rate", 150)
    engine.setProperty("rate", rate)
    engine.say(text)
    engine.runAndWait()

def run_chain(question: str) -> str:
    # Prepare chat history
    chat_history_text = "\n".join(
        [f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages]
    )

    # Generate response
    response_text = llm.invoke(prompt.format(chat_history=chat_history_text, question=question))

    # Store in memory
    st.session_state.chat_history.add_user_message(question)
    st.session_state.chat_history.add_ai_message(response_text)

    # Store in UI messages
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append({"role": "ai", "content": response_text})

    return response_text


with st.sidebar:
    st.image("https://img.icons8.com/color/96/robot-2.png", width=80)
    st.title("⚙️ Controls")

    st.session_state["rate"] = st.slider("Speech Rate", 100, 250, 150)
    st.session_state["auto_speak"] = st.checkbox("🔊 Auto Speak", True)

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history.clear()
        st.session_state.messages = []
        st.experimental_rerun()


st.title("🤖 Voice Assistant")
st.caption("Speak or type your question — the AI responds with context & voice.")

# Display chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])


user_text = st.text_input("💬 Type your message here:")
if st.button("Send") and user_text.strip():
    response = run_chain(user_text)
    if st.session_state.get("auto_speak", True):
        tts_speak(response)
    st.experimental_rerun()

# -------------------------------
# Voice Input
# -------------------------------
if st.button("🎤 Speak"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening...")
        audio = recognizer.listen(source)

    try:
        query = recognizer.recognize_google(audio)
        st.success(f"🧑 You said: {query}")
        response = run_chain(query)
        if st.session_state.get("auto_speak", True):
            tts_speak(response)
        st.experimental_rerun()
    except Exception as e:
        st.error(f"Speech recognition error: {e}")
