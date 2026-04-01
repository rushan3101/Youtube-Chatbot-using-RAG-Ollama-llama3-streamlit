import streamlit as st
from main import process_video, ask_question
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(page_title="YT Chatbot", layout="wide")

st.title("🎥 YouTube Video Chatbot (RAG + Ollama)")
st.caption("💬 Chat with any YouTube video using local LLM")

video_url = st.text_input("Enter YouTube Video URL")

# Initialize states
if "chain" not in st.session_state:
    st.session_state.chain = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# 🔥 Convert UI messages → LangChain messages
def format_chat_history(messages):
    history = []
    for msg in messages:
        if msg["role"] == "user":
            history.append(HumanMessage(content=msg["content"]))
        else:
            history.append(AIMessage(content=msg["content"]))
    return history


# Process video
if st.button("Process Video"):
    with st.spinner("Processing video..."):

        # RESET
        st.session_state.chain = None

        chain = process_video(video_url)

        if chain:
            st.session_state.chain = chain
            st.session_state.messages = []  # reset chat
            st.success("Video processed successfully!")
        else:
            st.error("Failed to process video.")


# Show chat only if chain exists
if st.session_state.chain:

    # Display previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask something about the video..."):

        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Convert history
        chat_history = format_chat_history(st.session_state.messages[-8:])  # last 8 messages for context

        # Stream response
        with st.chat_message("assistant"):
            response_container = st.empty()
            full_response = ""

            stream = ask_question(
                st.session_state.chain,
                prompt,
                chat_history
            )

            for chunk in stream:
                full_response += chunk
                response_container.markdown(full_response)

        # Save assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response
        })