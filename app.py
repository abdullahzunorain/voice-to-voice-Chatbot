import whisper
import os
from gtts import gTTS
from datetime import datetime
import tempfile
import streamlit as st
import soundfile as sf
import io
from groq import Groq

# Load a smaller Whisper model for faster processing
try:
    model = whisper.load_model("tiny")
except Exception as e:
    st.error(f"Error loading Whisper model: {e}")
    model = None

# Set up Groq API client using environment variable
GROQ_API_TOKEN = os.getenv("GROQ_API")
if not GROQ_API_TOKEN:
    st.error("Groq API token is missing. Set 'GROQ_API' in your environment variables.")
client = Groq(api_key=GROQ_API_TOKEN)

# Initialize the chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Function to get the LLM response from Groq with timeout handling
def get_llm_response(user_input, role="detailed responder"):
    prompt = f"As an expert, provide a detailed and knowledgeable response: {user_input}" if role == "expert" else \
             f"As a good assistant, provide a clear, concise, and helpful response: {user_input}" if role == "good assistant" else \
             f"Provide a thorough and detailed response: {user_input}"

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": user_input}],
            model="llama3-8b-8192",  # Replace with your desired model
            timeout=20  # Increased timeout to 20 seconds
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error during LLM response retrieval: {e}")
        return "Sorry, there was an error retrieving the response. Please try again."

# Function to convert text to speech using gTTS and handle temporary files
def text_to_speech(text):
    try:
        tts = gTTS(text)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            output_audio = temp_file.name
            tts.save(output_audio)
        return output_audio
    except Exception as e:
        st.error(f"Error generating TTS: {e}")
        return None

# Main chatbot function to handle audio input and output with chat history
def chatbot(audio):
    if not model:
        return "Error: Whisper model is not available.", None

    if audio is None:
        return "No audio provided. Please upload a valid audio file.", None

    try:
        # Step 1: Transcribe the audio using Whisper
        audio_data, sample_rate = sf.read(audio)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            sf.write(temp_file.name, audio_data, sample_rate)
            result = model.transcribe(temp_file.name)
            user_text = result.get("text", "")
            if not user_text.strip():
                return "Could not understand the audio. Please try speaking more clearly.", None

        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Display transcription in chat history
        st.session_state.chat_history.append((timestamp, "User", user_text))

        # Step 2: Get LLM response from Groq
        response_text = get_llm_response(user_text)

        # Step 3: Convert the response text to speech
        output_audio = text_to_speech(response_text)

        # Append the latest interaction to the chat history
        st.session_state.chat_history.append((timestamp, "Chatbot", response_text))

        # Format the chat history for display with timestamps and clear labels
        formatted_history = "\n".join([f"[{time}] {speaker}: {text}" for time, speaker, text in st.session_state.chat_history])
        
        return formatted_history, output_audio

    except Exception as e:
        st.error(f"Error in chatbot function: {e}")
        return "Sorry, there was an error processing your request.", None

# Streamlit app layout
st.title("Voice to Voice Chatbot")
st.write("Upload your audio, and the chatbot will transcribe and respond to it with a synthesized response.")

# Audio input
audio_file = st.file_uploader("Upload Audio", type=["wav", "mp3"])

if st.button("Submit"):
    if audio_file:
        chat_history, response_audio_path = chatbot(audio_file)

        # Display chat history
        st.text_area("Chat History", chat_history, height=300)

        # Play response audio
        if response_audio_path:
            st.audio(response_audio_path)

# Add CSS styling
st.markdown(
    """
    <style>
    body {
        background-image: url("https://huggingface.co/spaces/abdullahzunorain/voice-to-voice-Chatbot/resolve/main/BG_1.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        color: white;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stButton > button {
        background-color: #FFD700;
        color: black;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #FFC107;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

