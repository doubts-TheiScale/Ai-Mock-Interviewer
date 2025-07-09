import streamlit as st 
from gtts import gTTS
from pydub import AudioSegment
import tempfile
import os
import speech_recognition as sr
from transformers import pipeline as pl
import asyncio
import edge_tts

def text_to_speech(text, c=0, voice="en-US-JennyNeural"):
    output_file = f"output{c}.mp3"
    
    async def run_tts():
        communicate = edge_tts.Communicate(text=text, voice=voice)
        await communicate.save(output_file)
    
    asyncio.run(run_tts())
    return output_file



import datetime

def transcribe(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        file_path = tmpfile.name
        tmpfile.write(uploaded_file.read())

    # Convert audio to required format
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(file_path, format="wav")

    # ✅ Generate a unique file name using timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = uploaded_file.name.replace(" ", "_")
    unique_file_name = f"{safe_name}_{timestamp}.wav"

    # Upload to Google Drive
    drive_link = upload_audio_to_drive(file_path, unique_file_name)
    st.success(f"✅ Audio uploaded to Google Drive: [View File]({drive_link})")

    # Transcribe
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        st.info("🔄 Transcribing... Please wait!")
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            os.remove(file_path)
            return text
        except sr.UnknownValueError:
            st.sidebar.error("❌ Could not understand the audio.")
        except sr.RequestError:
            st.sidebar.error("❌ API error. Check internet connection.")

    os.remove(file_path)
    return ""
