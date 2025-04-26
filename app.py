import streamlit as st
from textblob import TextBlob
import ollama
import speech_recognition as sr  # Voice input
import os
from gtts import gTTS  # Google Text-to-Speech
import pandas as pd  # For mood chart

# 🌈 Custom page styling
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #e0f7fa, #f1f8e9);
        font-family: 'Segoe UI', sans-serif;
        color: #333333;
    }

    h1, h2, h3 {
        color: #2e7d32;
    }

    .stTextInput>div>div>input {
        background-color: #ffffff;
        color: #333333;
    }

    .stButton>button {
        background-color: #81c784;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
        font-weight: bold;
    }

    .stButton>button:hover {
        background-color: #66bb6a;
    }

    .stSidebar {
        background-color: #f0f4c3;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to generate a response from GPT model
def generate_response(prompt):
    try:
        response = ollama.chat(
            model="tinyllama",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}]
        )
        return response['message']['content'].strip()
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Analyze sentiment
def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.5:
        return "Very Positive", polarity
    elif 0.1 < polarity <= 0.5:
        return "Positive", polarity
    elif -0.1 <= polarity <= 0.1:
        return "Neutral", polarity
    elif -0.5 < polarity < -0.1:
        return "Negative", polarity
    else:
        return "Very Negative", polarity

# Provide coping strategies
def provide_coping_strategy(sentiment):
    strategies = {
        "Very Positive": "Keep up the positive vibes! Consider sharing your good mood with others.",
        "Positive": "It's great to see you're feeling positive. Keep doing what you're doing!",
        "Neutral": "It's alright to feeling this way. We're with you every step of the way.",
        "Negative": "It seems you're feeling down. Try to take a break and do something relaxing.",
        "Very Negative": "I'm sorry to hear that you're feeling very negative. Consider talking to a friend or seeking professional help."
    }
    return strategies.get(sentiment, "Keep going, you're doing great!")

# Function to handle speech using gTTS
def speak_text_gtts(text, filename='response.mp3'):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    return filename

# Disclaimer regarding data privacy
def display_disclaimer():
    st.sidebar.markdown(
        "<h2 style='color: #FF5733;'>Data Privacy Disclaimer</h2>",
        unsafe_allow_html=True
    )
    st.sidebar.markdown(
        "<span style='color: #FF5733;'>This application stores your session data, including your messages and "
        "sentiment analysis results, in temporary storage during your session. "
        "This data is not stored permanently and is used solely to improve your interaction with the chatbot. "
        "Please avoid sharing personal or sensitive information during your conversation.</span>",
        unsafe_allow_html=True
    )

# Set title for the page
st.title("AI-Therapist")

# Welcome Page
st.markdown("""
    <div style='text-align: left;'>
        <h3 style='color: #4CAF50; font-size: 20px;'>Hi, I’m your AI-Therapist</h3>
        <p style='color: #2196F3; font-size: 20px;'>How are you feeling today? I am here to listen!</p>
    </div>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'mood_tracker' not in st.session_state:
    st.session_state['mood_tracker'] = []
if 'transcribed_text' not in st.session_state:
    st.session_state['transcribed_text'] = ""
if 'last_response' not in st.session_state:
    st.session_state['last_response'] = ""

# Chat input form
with st.form(key='chat_form'):
    user_message = st.text_input("You:", value=st.session_state.get("transcribed_text", ""), key="user_input")

    # Buttons
    submit_button = st.form_submit_button(label='Send')
    speak_button = st.form_submit_button("🎤Speak")
    play_button = st.form_submit_button("🔊Play Audio")

    if speak_button:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening...")
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)
                st.session_state["transcribed_text"] = text
                st.success(f"You said: {text}")
            except sr.UnknownValueError:
                st.error("Sorry, I could not understand your speech.")
            except sr.RequestError:
                st.error("Speech service error.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    if play_button and st.session_state.get('last_response'):
        # Play audio of the last response
        filename = speak_text_gtts(st.session_state['last_response'])
        st.audio(filename, format='audio/mp3')

# When user submits a message
if submit_button and user_message:
    st.session_state['transcribed_text'] = ""
    st.session_state['messages'].clear()
    st.session_state['messages'].append(("You", user_message))

    sentiment, polarity = analyze_sentiment(user_message)
    coping_strategy = provide_coping_strategy(sentiment)
    st.session_state['coping_strategy'] = coping_strategy

    response = generate_response(user_message)
    st.session_state['last_response'] = response

    st.session_state['messages'].append(("Therapist", response))
    st.session_state['mood_tracker'].append((user_message, sentiment, polarity))

# Display chat messages
for sender, message in st.session_state['messages']:
    st.text(f"{sender}: {message}")

# Display coping strategies
if 'coping_strategy' in st.session_state:
    st.write(f"Suggested Coping Strategy: {st.session_state['coping_strategy']}")

# Display resources
st.sidebar.title("Resources")
st.sidebar.write("If you need immediate help, please contact one of the following resources:")
st.sidebar.write("1. 1Life, Crisis Support, Suicide Prevention: 78930-78930")
st.sidebar.write("2. Lifeline Foundation: 90888030303")
st.sidebar.write("3. Aasra: 9820466726")
st.sidebar.write("[More Resources](https://telemanas.mohfw.gov.in/home)")

# Display session summary with mood chart
if st.sidebar.button("Show Session Summary"):
    st.sidebar.write("### Session Summary")
    for i, (message, sentiment, polarity) in enumerate(st.session_state['mood_tracker']):
        st.sidebar.write(f"{i + 1}. {message} - Sentiment: {sentiment} (Polarity: {polarity})")

    # Plot sentiment polarity over time
    if st.session_state['mood_tracker']:
        df = pd.DataFrame(st.session_state['mood_tracker'], columns=["Message", "Sentiment", "Polarity"])
        st.sidebar.write("#### Mood Tracker Chart")
        st.sidebar.line_chart(df["Polarity"])
