import speech_recognition as sr
import pyttsx3
import time
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM


# Load AI Model
llm = OllamaLLM(model="mistral") 

# Initialize Memory (LangChain v1.0+)
chat_history = ChatMessageHistory()

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()
engine.setProperty("rate", 160)  # Adjust speaking speed

# Speech Recognition
recognizer = sr.Recognizer()

# Function to Speak (chunked, sentence by sentence)
def speak(text: str):
    if text and isinstance(text, str):
        print(f"\n🔊 Speaking...\n")
        # Split into sentences/paragraphs
        for part in text.split("\n"):
            if part.strip():
                engine.say(part.strip())
        engine.runAndWait()  #  Wait until finished speaking
        time.sleep(0.5)      # Small pause before listening again
    else:
        print("⚠️ No valid text to speak.")

# Function to Listen
def listen():
    with sr.Microphone() as source:
        print("\n🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio)
        print(f"👂 You Said: {query}")
        return query.lower()
    except sr.UnknownValueError:
        print("🤖 Sorry, I couldn't understand. Try again!")
        return ""
    except sr.RequestError:
        print("⚠️ Speech Recognition Service Unavailable")
        return ""

# AI Chat Prompt
prompt = PromptTemplate(
    input_variables=["chat_history", "question"],
    template="Previous conversation:\n{chat_history}\n\nUser: {question}\nAI:"
)

# Function to Process AI Responses
def run_chain(question: str) -> str:
    # Retrieve past chat history
    chat_history_text = "\n".join(
        [f"{msg.type.capitalize()}: {msg.content}" for msg in chat_history.messages]
    )

    # Run AI response generation (Ollama returns plain string)
    response_text = llm.invoke(
        prompt.format(chat_history=chat_history_text, question=question)
    )

    # Store new user input and AI response in memory
    chat_history.add_user_message(question)
    chat_history.add_ai_message(response_text)

    return response_text


# Main Loop
speak("Hello! I am your AI Assistant. How can I help you today?")
while True:
    query = listen()
    if "exit" in query or "stop" in query:
        speak("Goodbye! Have a great day.")
        break
    if query:
        response = run_chain(query)
        print(f"\n🤖 AI Response:\n{response}\n")
        speak(response)   # Only after finishing this, mic opens again
