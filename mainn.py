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
GROQ_API_KEY = "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"

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

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
st.title("AI Chatbot with Audio Input and Output")

# Audio file uploader
uploaded_audio = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a"])

if uploaded_audio:
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:
        temp_audio_file.write(uploaded_audio.read())
        temp_audio_path = temp_audio_file.name

    # Step 1: Transcribe the audio using Whisper
    result = model.transcribe(temp_audio_path)
    user_text = result["text"]
    
    # Display transcribed text
    st.write("You said:", user_text)

    # Step 2: Get LLM response from Groq
    response_text = get_llm_response(user_text)

    # Display LLM response text
    st.write("Bot response:", response_text)

    # Step 3: Convert the response text to speech
    output_audio = text_to_speech(response_text)

    # Play the audio response
    audio_file = open(output_audio, "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp3")

    # Clean up temporary files
    os.remove(temp_audio_path)
    os.remove(output_audio)
