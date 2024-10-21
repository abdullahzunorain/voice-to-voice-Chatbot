import os
import json
import streamlit as st
import speech_recognition as sr
import pyttsx3  # for converting text to speech
from gtts import gTTS  # another option for text-to-speech
from groq import Groq
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO

# Streamlit page configuration
st.set_page_config(
    page_title="ChatLlama 🦙",
    page_icon="🦙",
    layout="centered"
)

# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function to convert text to speech
def text_to_speech(text):
    # Using pyttsx3 (offline TTS engine)
    engine.say(text)
    engine.runAndWait()

    # Alternatively, using Google Text-to-Speech (online TTS engine)
    # tts = gTTS(text)
    # tts.save("response.mp3")
    # st.audio("response.mp3")

# Function to convert speech to text
def speech_to_text(audio_file):
    try:
        # Load the audio file with SpeechRecognition
        audio_data = sr.AudioFile(audio_file)
        with audio_data as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.record(source)

        # Convert speech to text
        user_input_text = recognizer.recognize_google(audio)
        return user_input_text

    except sr.UnknownValueError:
        return "Sorry, I couldn't understand that."
    except sr.RequestError:
        return "Sorry, my speech service is down."

# Get the API key from Streamlit secrets
API_KEY = st.secrets["GROQ_API_KEY"]

# Initialize the Groq client with the API key
client = Groq(api_key=API_KEY)

# Initialize the chat history as Streamlit session state if not present already
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Add custom CSS to center elements and change text color
st.markdown("""
    <style>
    .center-text {
        text-align: center;
    }
    .grey-text {
        color: #808080; /* Light grey */
    }
    </style>
    """, unsafe_allow_html=True)

# Centered Chatbot name
st.markdown("<h1 class='center-text'>ChatLlama 🦙</h1>", unsafe_allow_html=True)

# Powered by text in grey, not as a heading
st.markdown("<p class='center-text grey-text'>Powered by Llama 3.1-70b</p>", unsafe_allow_html=True)

# Display a centered prompt above the input field
st.markdown("<h4 class='center-text'>What can I help with?</h4>", unsafe_allow_html=True)

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Upload audio file for input
audio_file = st.file_uploader("Upload your voice", type=["wav", "mp3", "ogg"])

# If an audio file is uploaded, process it
if audio_file is not None:
    st.audio(audio_file)

    # Convert the speech to text
    user_prompt = speech_to_text(audio_file)

    if user_prompt:
        # Display the user input in the chat interface
        st.chat_message("user").markdown(user_prompt)
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})

        # Send the user's message to the Llama model and get the response
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            *st.session_state.chat_history
        ]

        try:
            # Query the Llama model using Groq API
            response = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=messages
            )
            assistant_response = response.choices[0].message.content
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

            # Display the assistant's response in the chat interface
            st.chat_message("assistant").markdown(assistant_response)

            # Convert the assistant's text response to speech
            st.write("Assistant is speaking...")
            text_to_speech(assistant_response)

        except Exception as e:
            st.error(f"An error occurred: {e}")

# Voice-to-voice chatbot logic completed.

