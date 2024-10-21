# import os
# import json
# import streamlit as st
# import speech_recognition as sr
# from gtts import gTTS  # Google Text-to-Speech
# from pydub import AudioSegment
# from pydub.playback import play
# from io import BytesIO
# from groq import Groq

# # Streamlit page configuration
# st.set_page_config(
#     page_title="ChatLlama 🦙",
#     page_icon="🦙",
#     layout="centered"
# )

# # Initialize the speech recognizer
# recognizer = sr.Recognizer()

# # Function to convert text to speech using gTTS
# def text_to_speech(text):
#     try:
#         tts = gTTS(text)
#         audio_fp = BytesIO()
#         tts.write_to_fp(audio_fp)
#         audio_fp.seek(0)

#         # Convert the audio to a format compatible with Streamlit's audio player
#         audio = AudioSegment.from_file(audio_fp, format="mp3")
#         play(audio)

#         # Optionally, save the speech as an audio file
#         # tts.save("response.mp3")
#         # st.audio("response.mp3")
#     except Exception as e:
#         st.error(f"Error in converting text to speech: {e}")

# # Function to convert speech to text
# def speech_to_text(audio_file):
#     try:
#         audio_data = sr.AudioFile(audio_file)
#         with audio_data as source:
#             recognizer.adjust_for_ambient_noise(source)
#             audio = recognizer.record(source)

#         # Convert speech to text
#         user_input_text = recognizer.recognize_google(audio)
#         return user_input_text

#     except sr.UnknownValueError:
#         return "Sorry, I couldn't understand that."
#     except sr.RequestError:
#         return "Sorry, my speech service is down."

# # Get the API key from Streamlit secrets
# API_KEY = st.secrets["GROQ_API_KEY"]

# # Initialize the Groq client with the API key
# client = Groq(api_key=API_KEY)

# # Initialize the chat history as Streamlit session state if not present already
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# # Add custom CSS to center elements and change text color
# st.markdown("""
#     <style>
#     .center-text {
#         text-align: center;
#     }
#     .grey-text {
#         color: #808080; /* Light grey */
#     }
#     </style>
#     """, unsafe_allow_html=True)

# # Centered Chatbot name
# st.markdown("<h1 class='center-text'>ChatLlama 🦙</h1>", unsafe_allow_html=True)

# # Powered by text in grey, not as a heading
# st.markdown("<p class='center-text grey-text'>Powered by Llama 3.1-70b</p>", unsafe_allow_html=True)

# # Display a centered prompt above the input field
# st.markdown("<h4 class='center-text'>What can I help with?</h4>", unsafe_allow_html=True)

# # Display chat history
# for message in st.session_state.chat_history:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Upload audio file for input
# audio_file = st.file_uploader("Upload your voice", type=["wav", "mp3", "ogg"])

# # If an audio file is uploaded, process it
# if audio_file is not None:
#     st.audio(audio_file)

#     # Convert the speech to text
#     user_prompt = speech_to_text(audio_file)

#     if user_prompt:
#         # Display the user input in the chat interface
#         st.chat_message("user").markdown(user_prompt)
#         st.session_state.chat_history.append({"role": "user", "content": user_prompt})

#         # Send the user's message to the Llama model and get the response
#         messages = [
#             {"role": "system", "content": "You are a helpful assistant"},
#             *st.session_state.chat_history
#         ]

#         try:
#             # Query the Llama model using Groq API
#             response = client.chat.completions.create(
#                 model="llama-3.1-70b-versatile",
#                 messages=messages
#             )
#             assistant_response = response.choices[0].message.content
#             st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

#             # Display the assistant's response in the chat interface
#             st.chat_message("assistant").markdown(assistant_response)

#             # Convert the assistant's text response to speech
#             st.write("Assistant is speaking...")
#             text_to_speech(assistant_response)

#         except Exception as e:
#             st.error(f"An error occurred: {e}")






import streamlit as st
from groq import Groq
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play

# Streamlit page configuration
st.set_page_config(
    page_title="ChatLlama 🦙",
    page_icon="🦙",
    layout="centered"
)

# Check if the API key is in Streamlit secrets
if "GROQ_API_KEY" not in st.secrets:
    st.error("The GROQ API Key is missing! Please add it to your Streamlit secrets.")
    st.stop()

# Get the API key from Streamlit secrets
API_KEY = st.secrets["GROQ_API_KEY"]

# Initialize the Groq client with the API key
client = Groq(api_key=API_KEY)

# Initialize recognizer
recognizer = sr.Recognizer()

# Function to convert audio to WAV if necessary
def convert_to_wav(uploaded_audio):
    try:
        # Load the audio file using pydub
        audio = AudioSegment.from_file(uploaded_audio)
        wav_io = BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)  # Reset the pointer to the start of the BytesIO object
        return wav_io
    except Exception as e:
        st.error(f"Failed to process the audio file: {e}")
        return None

# Function to convert speech to text
def speech_to_text(audio_file):
    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except Exception as e:
        st.error(f"Error processing audio file: {e}")
        return None

# Function to convert text to speech
def text_to_speech(text):
    tts = gTTS(text)
    audio_io = BytesIO()
    tts.save(audio_io, format="mp3")
    audio_io.seek(0)
    return audio_io

# Display ChatLlama title and prompt
st.markdown("<h1 class='center-text'>ChatLlama 🦙</h1>", unsafe_allow_html=True)
st.markdown("<p class='center-text grey-text'>Powered by Llama 3.1-70b</p>", unsafe_allow_html=True)
st.markdown("<h4 class='center-text'>What can I help with?</h4>", unsafe_allow_html=True)

# Upload audio file
audio_file = st.file_uploader("Upload your voice", type=["wav", "mp3", "ogg"])

if audio_file is not None:
    st.audio(audio_file, format="audio/mp3")

    # Convert to WAV format for processing
    wav_audio = convert_to_wav(audio_file)
    
    if wav_audio:
        # Convert speech to text
        user_prompt = speech_to_text(wav_audio)

        if user_prompt:
            st.markdown(f"**You said:** {user_prompt}")

            # Append user's message to the chat history
            st.session_state.chat_history.append({"role": "user", "content": user_prompt})

            # Send user's message to the LLM and get a response
            messages = [
                {"role": "system", "content": "You are a helpful assistant"},
                *st.session_state.chat_history
            ]

            response = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=messages
            )

            assistant_response = response.choices[0].message.content
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

            # Display the LLM's response
            st.markdown(f"**Llama:** {assistant_response}")

            # Convert the LLM's response to speech and play it
            speech_audio = text_to_speech(assistant_response)
            st.audio(speech_audio, format="audio/mp3")
