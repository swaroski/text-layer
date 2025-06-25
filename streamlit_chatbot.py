import streamlit as st
import requests

API_URL = "http://localhost:8000/v1/text-to-sql/"

# Layout and style
st.set_page_config(page_title="TextLayer Text-to-SQL Chatbot", layout="wide")

st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .custom-input input {
        background-color: #f9f9fc;
        border: 2px solid #4A90E2;
        border-radius: 8px;
        padding: 10px;
        font-size: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💬 TextLayer Text-to-SQL Chatbot")

# Init message state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Handle submission
def handle_submit():
    user_input = st.session_state.chatbox.strip()
    if not user_input:
        return

    # Append user message (no need to render here)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Thinking..."):
        try:
            resp = requests.post(API_URL, json={"question": user_input}, timeout=60)
            data = resp.json()

            if resp.status_code == 200 and "payload" in data:
                payload = data["payload"]
                summary = payload.get("summary", "")
                sql = payload.get("sql_query", "")
                result_md = payload.get("result_markdown", "")

                response = ""
                if summary:
                    response += f"**:memo: Summary:**\n{summary}\n\n"
                if sql:
                    response += f"**SQL Used:**\n```sql\n{sql}\n```\n"
                if result_md:
                    response += f"**Result:**\n{result_md}"

                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                err = data.get("error", "Unknown error")
                st.session_state.messages.append({"role": "assistant", "content": f":x: {err}"})
        except Exception as ex:
            err_msg = f":x: Failed to reach backend: {ex}"
            st.session_state.messages.append({"role": "assistant", "content": err_msg})

    st.session_state.chatbox = ""


# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input (now with key + on_change)
st.text_input(
    "Ask a question about your data...",
    key="chatbox",
    on_change=handle_submit,
    label_visibility="collapsed",
    placeholder="Ask a question about your data..."
)
