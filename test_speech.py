from gtts import gTTS
import streamlit as st
import os

# Simulate dynamic response (you can replace this with session state if needed)
response_text = "Hello, I'm your AI therapist. How are you feeling today?"
audio_file = "response.mp3"

# Display the AI message
st.write(f"AI Therapist: {response_text}")

# Show the button to generate & play audio
if st.button("🔊 Play Audio"):
    # Always recreate the audio file on button press (optional: check if file exists to save time)
    tts = gTTS(text=response_text, lang='en')
    tts.save(audio_file)

    # Show the player (user has to press ▶ manually — this is normal)
    audio_bytes = open(audio_file, "rb").read()
    st.audio(audio_bytes, format="audio/mp3")
