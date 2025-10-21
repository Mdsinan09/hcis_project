import streamlit as st
import random
import time

# -----------------------------------------------------------------
# 💬 AI Chatbot Interface
# -----------------------------------------------------------------
def chatbot_ui():
    st.title("🤖 AI Chatbot Assistant")
    st.markdown("Ask me anything about **Deepfake Detection**, **AI Hallucination**, or **Multimedia Analysis** 🎯")

    # Session state for chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # User input
    user_input = st.text_input("💬 Type your question here:")

    # Generate response
    if user_input:
        st.session_state.chat_history.append(("You", user_input))
        with st.spinner("Thinking... 🤔"):
            time.sleep(1.5)
            bot_response = generate_response(user_input)
        st.session_state.chat_history.append(("Bot", bot_response))

    # Chat history display
    st.markdown("---")
    for sender, message in st.session_state.chat_history:
        if sender == "You":
            st.markdown(f"🧑 **{sender}:** {message}")
        else:
            st.markdown(f"🤖 **{sender}:** {message}")

    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()


# -----------------------------------------------------------------
# 🧠 Chatbot Response Logic
# -----------------------------------------------------------------
def generate_response(user_input):
    user_input = user_input.lower()

    # --- Deepfake Detection Related ---
    if "detect" in user_input or "fake" in user_input or "deepfake" in user_input:
        responses = [
            "We analyze facial inconsistencies, lip-sync accuracy, and compression artifacts to detect fake videos 🎥.",
            "Our system compares **audio**, **video**, and **text patterns** to identify manipulated or AI-generated content 🧩.",
            "By using computer vision and audio analysis, we detect subtle frame-level artifacts in deepfakes 🔍."
        ]

    # --- AI Hallucination / Text Analysis ---
    elif "hallucination" in user_input or "text" in user_input or "language" in user_input:
        responses = [
            "AI hallucination occurs when models generate false or unsupported statements 🤖.",
            "We check factual accuracy using a semantic database and multilingual truth verification 🌐.",
            "Our text analyzer compares your text against trusted data sources to estimate its reliability score 📜."
        ]

    # --- Audio or Voice Deepfake ---
    elif "audio" in user_input or "voice" in user_input or "sound" in user_input:
        responses = [
            "We use **MFCC features** and frequency analysis to detect cloned or synthetic voices 🎧.",
            "Synthetic voices often lack natural pitch variation — our system detects those patterns 📊.",
            "We analyze voiceprints and acoustic features to find deepfake or AI-generated voices 🔈."
        ]

    # --- Video Analysis ---
    elif "video" in user_input or "frame" in user_input:
        responses = [
            "Each video frame is analyzed for **face morphing, blur artifacts**, and **lip-sync mismatches** 🎬.",
            "Our vision engine checks consistency across frames to find visual manipulations 🧠.",
            "We extract keyframes and look for compression and lighting inconsistencies to detect deepfakes 📸."
        ]

    # --- General System Questions ---
    elif "how" in user_input or "what" in user_input or "explain" in user_input:
        responses = [
            "The system performs multimodal analysis — combining results from video, audio, and text for higher accuracy 📈.",
            "We integrate AI and signal processing techniques to ensure reliable detection 🔍.",
            "Our fusion engine assigns weights to each detection result and gives a final authenticity score ⚖️."
        ]

    # --- Greetings / Miscellaneous ---
    elif "hello" in user_input or "hi" in user_input or "hey" in user_input:
        responses = [
            "Hello 👋! How can I assist you with deepfake or AI detection today?",
            "Hey there! Ready to explore how our system detects deepfakes? 🎥",
            "Hi! You can ask me about deepfake detection, audio analysis, or AI hallucinations 💬."
        ]

    else:
        responses = [
            "Hmm, I'm not sure about that — could you rephrase your question? 🤔",
            "That’s interesting! Try asking me something about deepfake detection, AI hallucination, or text reliability 📚.",
            "I didn’t quite get that — maybe you want to know how our detector works? 🧠"
        ]

    return random.choice(responses)
        