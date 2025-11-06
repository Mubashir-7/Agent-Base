import streamlit as st
import speech_recognition as sr
import pyttsx3
import tempfile
import os
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM



llm = OllamaLLM(model="mistral") 
recognizer = sr.Recognizer()
engine = pyttsx3.init()


if 'chat' not in st.session_state:
    st.session_state.chat = []  
if 'settings' not in st.session_state:
    st.session_state.settings = {
        'tts_rate': 160,
        'auto_speak': True,
        'pause_after_speak': 0.4,
    }

# Apply TTS settings
engine.setProperty('rate', st.session_state.settings['tts_rate'])



def tts_save_and_play(text: str):
    if not text:
        return None
    try:
        engine.say(text)
        engine.runAndWait()
        return None
    except Exception as e:
        st.warning(f"TTS failed locally: {e}")
        return None


def transcribe_audio_file(file_path: str) -> str:
    try:
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return ""
    except Exception as e:
        st.error(f"Transcription error: {e}")
        return ""

prompt = PromptTemplate(
    input_variables=["chat_history", "question"],
    template="Previous conversation:\n{chat_history}\n\nUser: {question}\nAI:"
)

def run_chain(question: str) -> str:
    chat_history_text = "\n".join([f"{role}: {text}" for role, text in st.session_state.chat])
    response_text = llm.invoke(prompt.format(chat_history=chat_history_text, question=question))
    st.session_state.chat.append(("User", question))
    st.session_state.chat.append(("AI", response_text))
    return response_text


st.markdown(
    """
    <style>
    body {background-color: #f5f7fa;}
    .main {background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0px 4px 12px rgba(0,0,0,0.1);} 
    .chat-bubble-user {background-color: #0084ff; color: white; padding: 10px 15px; border-radius: 20px; margin: 8px 0; max-width: 80%;}
    .chat-bubble-ai {background-color: #f1f0f0; color: black; padding: 10px 15px; border-radius: 20px; margin: 8px 0; max-width: 80%;}
    .header-logo {text-align: center; margin-bottom: 20px;}
    .header-logo img {width: 100px; border-radius: 50%;}
    .header-title {text-align: center; font-size: 36px; font-weight: 700; color: #333; margin-bottom: 5px;}
    .header-subtitle {text-align: center; font-size: 16px; color: #666; margin-bottom: 30px;}
    </style>
    """,
    unsafe_allow_html=True
)


st.set_page_config(page_title="Voice Assistant — Streamlit WebUI", layout="wide")

st.markdown('<div class="header-logo"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/OOjs_UI_icon_speech.svg/1024px-OOjs_UI_icon_speech.svg.png"></div>', unsafe_allow_html=True)
st.markdown('<div class="header-title">AI Voice Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Talk, Type, or Upload Audio — Your Smart Assistant</div>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Conversation")
    chat_container = st.container()
    with chat_container:
        for role, txt in st.session_state.chat:
            if role == 'User':
                st.markdown(f'<div class="chat-bubble-user">{txt}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble-ai">{txt}</div>', unsafe_allow_html=True)

    st.markdown("---")
    user_text = st.text_input("✍️ Type your message here")
    send_btn = st.button("Send")

    st.write("or")
    uploaded_file = st.file_uploader("🎵 Upload an audio file (wav/mp3)")
    use_server_mic = st.button("🎤 Use microphone (local only)")

with col2:
    st.sidebar.header("⚙️ Settings")
    st.session_state.settings['tts_rate'] = st.sidebar.slider("TTS rate", 100, 220, st.session_state.settings['tts_rate'])
    st.session_state.settings['auto_speak'] = st.sidebar.checkbox("Auto speak AI responses", value=st.session_state.settings['auto_speak'])
    st.session_state.settings['pause_after_speak'] = st.sidebar.slider("Pause after speaking (seconds)", 0.0, 2.0, st.session_state.settings['pause_after_speak'])
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Quick actions**")
    if st.sidebar.button("🗑️ Clear conversation"):
        st.session_state.chat = []
        st.experimental_rerun()

engine.setProperty('rate', st.session_state.settings['tts_rate'])


if uploaded_file is not None:
    temp_audio_path = os.path.join(tempfile.gettempdir(), uploaded_file.name)
    with open(temp_audio_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    st.info("Transcribing uploaded audio...")
    transcribed = transcribe_audio_file(temp_audio_path)
    if transcribed:
        st.success(f"Transcribed: {transcribed}")
        response = run_chain(transcribed)
        st.experimental_rerun()
    else:
        st.error("Could not transcribe the uploaded audio.")


if use_server_mic:
    try:
        st.info("🎤 Recording from server microphone...")
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
        try:
            query = recognizer.recognize_google(audio)
            st.success(f"You said: {query}")
            response = run_chain(query)
            if st.session_state.settings['auto_speak']:
                tts_save_and_play(response)
            st.experimental_rerun()
        except sr.UnknownValueError:
            st.error("Could not understand audio")
    except Exception as e:
        st.error(f"Microphone error: {e}")


if send_btn and user_text:
    response = run_chain(user_text)
    if st.session_state.settings['auto_speak']:
        tts_save_and_play(response)
    st.experimental_rerun()

st.markdown("---")
st.caption("✨ Built with Streamlit, LangChain & Ollama — making AI conversations simple, beautiful, and powerful.")
