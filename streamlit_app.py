import streamlit as st
import json
from datetime import datetime
from main import ask_chatbot

# =====================================================

# PAGE CONFIG

# =====================================================

st.set_page_config(
page_title="AI Knowledge Assistant",
page_icon="🤖",
layout="wide",
initial_sidebar_state="expanded"
)

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

# =====================================================

# CUSTOM CSS

# =====================================================

st.markdown("""

<style>

/* Background */
.stApp {
    background-color: #0f172a;
}

/* Header */
.main-title {
    text-align: center;
    font-size: 3.5rem;
    font-weight: 800;
    color: white;
    margin-top: 10px;
    margin-bottom: 10px;
}

.subtitle {
    text-align: center;
    color: #94a3b8;
    font-size: 1rem;
    margin-bottom: 30px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827;
}

/* Chat Messages */
[data-testid="stChatMessage"] {
    border-radius: 18px;
    padding: 12px;
}

/* User Bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background-color: #1e293b;
}

/* Assistant Bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background-color: #111827;
}

/* Metrics */
[data-testid="stMetric"] {
    background-color: #1e293b;
    padding: 10px;
    border-radius: 12px;
}

/* Buttons */
.stButton > button {
    width: 100%;
    border-radius: 12px;
    height: 45px;
    font-weight: bold;
}

/* Footer */
footer {
    visibility: hidden;
}

</style>

""", unsafe_allow_html=True)

# =====================================================

# HEADER

# =====================================================

st.markdown(
    """
    <div class="main-title">
        🤖 AI Knowledge Assistant
    </div>

    <div class="subtitle">
        PostgreSQL • pgvector • MiniLM-L6-v2 • ChatGroq
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================

# SIDEBAR

# =====================================================

with st.sidebar:

    st.header("📊 System Information")

    st.metric(
        label="Knowledge Base",
        value="9,106 Records"
    )

    st.metric(
        label="Embedding Model",
        value="MiniLM-L6-v2"
    )

    st.metric(
        label="LLM",
        value="Llama 3.3 70B"
    )

    st.info(
    "🚀 RAG Chatbot Ready"
    )

    st.divider()

    st.subheader("🚀 Features")

    st.markdown("""
    * PostgreSQL Database
    * pgvector Similarity Search
    * Retrieval-Augmented Generation
    * Chat History
    * Context Retrieval
    * ChatGroq Integration
  """)

    st.divider()

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.rerun()  

    st.divider()

    st.subheader("📥 Export Chat")

    messages = st.session_state.get(
    "messages",
    []
    )

    if len(messages) > 0:

        chat_json = json.dumps(
            messages,
            indent=4,
            ensure_ascii=False
        )

        st.download_button(
            label="📄 Download Chat History",
            data=chat_json,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# =====================================================

# SESSION STATE

# =====================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =====================================================

# WELCOME MESSAGE

# =====================================================

if len(st.session_state.messages) == 0:

    st.info(
    """

### 👋 Welcome to AI Knowledge Assistant

Try asking:

• What are the steps in machine learning process?

• How to build a machine learning model?

• Explain supervised learning

• List open source AI projects
"""
)

# =====================================================

# DISPLAY CHAT HISTORY

# =====================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# =====================================================

# USER INPUT

# =====================================================

prompt = st.chat_input(
    "Ask a question..."
)


if prompt and isinstance(prompt, str):

    # ==========================
    # USER MESSAGE
    # ==========================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):

        st.markdown(prompt)

    # ==========================
    # ASSISTANT MESSAGE
    # ==========================

    with st.chat_message("assistant"):

        with st.spinner(
            "🔍 Retrieving relevant documents..."
        ):

            try:

                answer = ask_chatbot(
                    user_question=prompt,
                    chat_history=st.session_state.messages
                )   

            except Exception as e:

                answer = f"Error: {str(e)}"

        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )