# app.py
import streamlit as st
from bot import support_chat

st.set_page_config(page_title="Customer Support Chatbot", page_icon="💬")
st.title("💬 Customer Support Chatbot (Mistral)")
st.caption("Classification + Personalized Reply + Summarization")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

user_text = st.chat_input("Type your message...")

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            out = support_chat(user_text)

        st.markdown(out["reply"])
        st.markdown(f"**Category:** `{out['category']}`")
        st.markdown(f"**Summary:** {out['summary']}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": f"{out['reply']}\n\n**Category:** `{out['category']}`\n\n**Summary:** {out['summary']}"
    })
