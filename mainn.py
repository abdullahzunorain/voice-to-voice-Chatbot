import whisper
import os
from gtts import gTTS
import streamlit as st
from groq import Groq
import tempfile
import torchaudio

# Load Whisper model for transcription
model = whisper.load_model("base")

# Set Groq API Key
# GROQ_API_KEY = "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"
# Set up Groq API client using environment variable
GROQ_API_TOKEN = os.getenv("GROQ_API")
if not GROQ_API_TOKEN:
    st.error("Groq API token is missing. Set 'GROQ_API' in your environment variables.")
client = Groq(api_key=GROQ_API_TOKEN)

# Initialize Groq client
client = Groq(api_key=GROQ_API_TOKEN)

# CSS styling for a better interface
st.markdown("""
    <style>
        /* Background styling */
        .stApp {
            background-color: #f0f2f6;
            color: #333;
        }
        /* Chatbot box styling */
        .chat-box {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 15px;
            margin-top: 10px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
        }
        /* Text styling */
        .user-input, .bot-response {
            font-family: 'Arial', sans-serif;
            font-size: 1.1em;
            color: #444;
        }
        .user-input {
            font-weight: bold;
            color: #007ACC;
        }
        /* Button styling */
        .stButton>button {
            background-color: #007ACC;
            color: white;
            border-radius: 8px;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# Function to get the LLM response from Groq
def get_llm_response(user_input):
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": user_input}],
        model="llama3-8b-8192"  # Replace with your desired model
    )
    return chat_completion.choices[0].message.content

# Function to convert text to speech using gTTS
def text_to_speech(text, output_audio="output_audio.mp3"):
    tts = gTTS(text)
    tts.save(output_audio)
    return output_audio

# Streamlit interface for the chatbot
st.title("AI Chatbot with Voice Interaction 🎙️")
st.write("Speak to the AI Chatbot by uploading an audio file, and it will respond with both text and audio. Let's chat!")

# Audio file uploader
uploaded_audio = st.file_uploader("Upload your audio file (WAV, MP3, M4A):", type=["wav", "mp3", "m4a"])

if uploaded_audio:
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:
        temp_audio_file.write(uploaded_audio.read())
        temp_audio_path = temp_audio_file.name

    # Step 1: Transcribe the audio using Whisper
    st.markdown("<div class='chat-box user-input'>Processing your input... 🎧</div>", unsafe_allow_html=True)
    result = model.transcribe(temp_audio_path)
    user_text = result["text"]

    # Display transcribed text
    st.markdown(f"<div class='chat-box user-input'>You said: {user_text}</div>", unsafe_allow_html=True)

    # Step 2: Get LLM response from Groq
    response_text = get_llm_response(user_text)

    # Display LLM response text
    st.markdown(f"<div class='chat-box bot-response'>Bot response: {response_text}</div>", unsafe_allow_html=True)

    # Step 3: Convert the response text to speech
    output_audio = text_to_speech(response_text)

    # Play the audio response
    audio_file = open(output_audio, "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp3")

    # Clean up temporary files
    os.remove(temp_audio_path)
    os.remove(output_audio)

else:
    # If no audio is uploaded, provide guidance
    st.markdown("<div class='chat-box'>Please upload an audio file to start the conversation!</div>", unsafe_allow_html=True)
